# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Aperture photometry module."""

import numpy as np
from enum import Flag
from astropy import __version__ as astropy_version
from astropy.table import Table
from astropy.stats import SigmaClip
from photutils import __version__ as photutils_version
from photutils.aperture import CircularAperture, CircularAnnulus, ApertureStats
from photutils.centroids import centroid_com, centroid_quadratic, \
                                centroid_2dg, centroid_sources
from photutils.utils import calc_total_error, circular_footprint

from astropop import __version__ as astropop_version
from astropop.photometry.detection import median_fwhm
from astropop.logger import logger
from astropop.fits_utils import imhdus


__all__ = ['aperture_photometry', 'PhotometryFlags']


class PhotometryFlags(Flag):
    """Flags for aperture photometry. Do not subclass it."""

    # 1: At least one pixel in the aperture was removed or masked
    REMOVED_PIXEL_IN_APERTURE = 1 << 0
    # 2: At least one pixel in the aperture was interpolated
    INTERPOLATED_PIXEL_IN_APERTURE = 1 << 1
    # 4: At least one pixel in the aperture was out of bounds of the image
    OUT_OF_BOUNDS = 1 << 2
    # 8: Saturated pixel in aperture
    SATURATED_PIXEL_IN_APERTURE = 1 << 3
    # 16: At least one pixel in sky annulus was removed or masked
    REMOVED_PIXEL_IN_ANNULUS = 1 << 4
    # 32: At least one pixel in sky annulus was interpolated
    INTERPOLATED_PIXEL_IN_ANNULUS = 1 << 5
    # 64: At least one pixel in sky annulus was out of bounds of the image
    OUT_OF_BOUNDS_ANNULUS = 1 << 6
    # 128: Possible contamination from nearby sources in aperture
    NEARBY_SOURCES = 1 << 7
    # 256: Possible contamination from nearby sources in annulus
    NEARBY_SOURCES_ANNULUS = 1 << 8
    # 512: Source recentering have failed and the original position was used
    RECENTERING_FAILED = 1 << 9


def _calc_local_bkg(data, positions, r_in, r_out, error, bkg_method,
                    sigma_clip, pixel_flags, mask):
    """Compute the background annulus for aperture photometry."""
    ann_ap = CircularAnnulus(positions, r_in=r_in, r_out=r_out)

    # MMM method gets computed in another function
    sclip = None
    if sigma_clip is not None:
        sclip = SigmaClip(sigma=sigma_clip)

    ann_stats = ApertureStats(data, ann_ap, error=error, mask=mask,
                              sum_method='exact', sigma_clip=sclip)
    if bkg_method == 'mmm' or bkg_method == 'mode':
        bkg = ann_stats.mode
    elif bkg_method == 'median':
        bkg = ann_stats.median
    elif bkg_method == 'mean':
        bkg = ann_stats.mean
    else:
        raise ValueError(f'Invalid bkg_method: {bkg_method}')

    bkg_std = ann_stats.std
    bkg_area = ann_ap.area

    if pixel_flags is not None:
        # TODO: compute flags
        bkg_flags = [0]*len(positions)
    else:
        bkg_flags = [0]*len(positions)

    return bkg, bkg_std, bkg_area, bkg_flags


def _recenter_sources(data, x, y, r, limit, method, mask):
    """Recenter the sources using photutils.centroids."""
    if method == 'com':
        func = centroid_com
    elif method == 'gaussian':
        func = centroid_2dg
    elif method == 'quadratic':
        func = centroid_quadratic
    else:
        raise ValueError(f'Invalid recenter_method: {method}')

    new_x, new_y = centroid_sources(data, x, y, box_size=r*2+1, mask=mask,
                                    centroid_func=func,
                                    footprint=circular_footprint(r))

    # Compute the distance between the old and new positions
    diff_x = np.abs(new_x - x)
    diff_y = np.abs(new_y - y)
    diff = np.sqrt(diff_x**2 + diff_y**2)

    # Recenter only the sources with a distance smaller than the limit
    idx = np.where(diff < limit)[0]
    if len(idx) != 0:
        logger.info(f'{len(idx)} have failed on recentering.')
    x[idx] = new_x[idx]
    y[idx] = new_y[idx]

    # associate the error flag
    error = np.zeros(len(x))
    error[idx] = PhotometryFlags.RECENTERING_FAILED

    return x, y, error


def aperture_photometry(data, x, y, r='auto', r_ann='auto',
                        recenter_limit=None, recenter_method='com',
                        gain=1.0, bkg_error=None, mask=None,
                        bkg_method='mmm', bkg_sigma_clip=3.0,
                        pixel_flags=None, box_size=11):
    """Perform aperture photometry using sep. Output units (ADU or e-) will
    be the considered the same as input.

    This method just wraps the `~photutils.ApertureStats` method
    from photutils, assuming standard arguments and performing extra steps:

    - Calculate the total error (bkg+poisson) from input data, based on data
      and bkg_error.
    - It assumes the `'exact'` method of subpixel sampling.
    - Compute an optimal aperture radius, considering only the gaussian
      background-only error. This radius is defined as r=0.6731*GFWHM.
    - Use sigma clipping for annulus background calculation.
    - Perform photometry flags generation. See
      `~astropop.photometry.PhotometryFlags`.
    - Sources recentering using `~photutils.centroids` methods. Only performed
      if `recenter_limit` is not None.

    Most of the reduction is based on Astropy workshop sample notebooks [1]_.

    Parameters
    ----------
    data : `~numpy.ndarray`
        2D image data for photometry
    x, y : array_like
        Positions of the sources
    r : float, `'auto'` (optional)
        Aperture radius, in pixels. If 'auto', the value will be estimated
        based in the median gaussian FWHM of the sources in the image
        (r=0.6731*GFWHM).
        Default: 'auto'
    r_ann : array_like([float, float]), `'auto'` `None` (optional)
        Annulus radii (r_in, r_out) for local background extraction in pixels.
        If 'auto', the annulus will be set based on aperture as (4*r, 6*r).
        If None, no local background subtraction will be performed.
        Default: 'auto'
    recenter_limit : float (optional)
        Maximum distance allowed to recenter the apertures. If None, no
        recentering will be performed.
        Default: `None`
    recenter_method : 'com', 'gaussian' or 'quadratic' (optional)
        Algorithm to recenter the apertures. If None, no recentering will be
        performed. `'com'` method will use the center of mass of the aperture,
        `'gaussian'` will use a gaussian fit to the aperture and `'quadratic'`
        will use a quadratic fit to the aperture. See `~photutils.centroids`
        for more information.
        Default: 'com'
    gain : float (optional)
        Gain to correctly calculate the error.
        Default: 1.0
    bkg_error : float or `~numpy.ndarray` (optional)
        1-sigma gaussian error of the background-only error of input data.
        If None, zero will be used.
        Default: `None`
    mask : `~numpy.ndarray` (optional)
        Mask badpixels and problematic ccd areas.
        Default: `None`
    pixel_flags : `~numpy.ndarray` (optional)
        Array with flags for each pixel. If None, no flags will be used.
        Flags must follow the `~astropop.frametada.PixelMaskFlags` standard.
        Default: `None`
    bkg_method : 'mmm', 'mode', 'median' or 'mean' (optional)
        Algorith to calculate the background value. `'mode'` or `'mmm'`
        (mean, median, mode) are computed as (3*median - 2*mean) and
        should be better for populated fields. `'median'` and `'mean'`
        just compute these values in the annulus. All algorithms can use sigma
        clipping if ``bkg_sigma_clip`` is not None.
        Default: 'mmm'
    bkg_sigma_clip : float, tuple(float, float) or `None` (optional)
        Sigma clipping values for background calculation. If a tuple is
        provided, the first value will be used as lower sigma and the second
        as upper sigma. Only used if ``sky_algorithm='sigmaclip'``.
        Default: 3.0
    box_size : int (optional)
        Box size for median FWHM computation. Default is 11.

    Returns
    -------
    res_ap : `~astropy.table.Table`
        Table containing all aperture photometry informations.
        - ``x``, ``y``: centroids of the sources. If recentering is performed,
            these values will be different from input.
        - ``aperture``: aperture radius. Same for all sources.
        - ``flux``: flux of the sources with bkg subtracted
        - ``flux_error``: flux error of the sources with bkg subtracted
        - ``aperture_area``: effective aperture (considering mask) of the
          sources.
        - ``bkg``: background value by pixel
        - ``bkg_stddev``: background standard deviation inside the annulus
        - ``bkg_area``: effective area of the annulus (considering mask and
          clipping)
        - ``flags``: flag for the sources
        - ``original_x``, ``original_y``: original input positions
        - ``fwhm``: circularized FWHM computed for each source
        The metadata of the table will contain the following information:
        - ``photutils``: photutils version used
        - ``astropy``: astropy version used
        - ``astropop``: astropop version used
        - ``fwhm``: median FWHM of the sources
        - ``r``: aperture radius used
        - ``r_in``: inner annulus radius used
        - ``r_out``: outer annulus radius used

    Notes
    -----
    - The input data is divided by the gain prior to any calculation.
    - The centroid of the sources is computed within a circular footprint with
      radius ``2*r+1``. See `~photutils.centroids.centroid_sources` for more
      information.
    - Local background subtraction is performed entirely by photutils. So,
      we do not touch it or compute any errors here.

    References
    ----------
    .. [1] Astropy workshop sample notebook
        (https://github.com/astropy/astropy-workshop/blob/9eec8aeb04cec0de4ae\
         8a5056449b92ca4019e16/09-Photutils/03-aperture_local_bkgsub.ipynb)
    """
    res_ap = Table()

    if isinstance(data, imhdus):
        data = data.data

    # data must be divided by gain. Also force a new instance
    data = np.array(data)/gain

    # copy x and y to avoid changing the original
    nx = np.array(x)
    ny = np.array(y)

    flags = np.zeros(len(x), dtype=np.int16)

    # compute median fwhm for all sources
    fwhm = median_fwhm(data, x, y, box_size=box_size, model='gaussian')

    # compute the automated aperture radius
    if r == 'auto':
        logger.debug('Aperture r set as `auto`. Calculating from FWHM.')
        r = 0.6371*fwhm
        res_ap.meta['r_auto'] = True
        logger.debug(f'FWHM:{fwhm} r:{r}')

    # compute the automated annulus radius
    if r_ann == 'auto':
        r_in = 4*r
        r_out = 6*r
        res_ap.meta['r_ann_auto'] = True
    elif r_ann is None:
        r_in = r_out = None
    else:
        r_in, r_out = r_ann

    if recenter_limit is not None:
        logger.debug('Recentering sources.')
        nx, ny, r_err = _recenter_sources(data, nx, ny, r,
                                          limit=recenter_limit,
                                          method=recenter_method,
                                          mask=mask)
        flags |= r_err

    positions = np.array(list(zip(nx, ny)))

    if bkg_error is None:
        bkg_error = 0.0

    # Get the total error (bkg+poisson) from photutils
    error = calc_total_error(data, bkg_error=bkg_error, effective_gain=gain)

    # Compute the local background of the sources
    if r_ann is not None:
        bkg, bkg_std, bkg_area, bkg_flags = _calc_local_bkg(
            data, positions, r_in, r_out, error=error, mask=mask,
            bkg_method=bkg_method, sigma_clip=bkg_sigma_clip,
            pixel_flags=pixel_flags
        )
        flags |= bkg_flags
    else:
        bkg = None

    # Calculate the sources apertures
    ap = CircularAperture(positions, r=r)
    ap_stats = ApertureStats(data, ap, error=error, mask=mask,
                             sum_method='exact', local_bkg=bkg)

    res_ap['x'] = x
    res_ap['y'] = y
    res_ap['aperture'] = [r]*len(x)
    res_ap['flux'] = ap_stats.sum
    res_ap['flux_error'] = ap_stats.sum_err
    res_ap['aperture_area'] = ap_stats.sum_aper_area
    res_ap['bkg'] = bkg
    res_ap['bkg_stddev'] = bkg_std
    res_ap['bkg_area'] = bkg_area
    res_ap['flags'] = flags
    res_ap['original_x'] = x
    res_ap['original_y'] = y
    res_ap['fwhm'] = ap_stats.fwhm
    res_ap['eccentricity'] = ap_stats.eccentricity

    res_ap.meta['photutils'] = photutils_version
    res_ap.meta['astropy'] = astropy_version
    res_ap.meta['astropop'] = astropop_version
    res_ap.meta['r'] = r
    res_ap.meta['r_in'] = r_in
    res_ap.meta['r_out'] = r_out
    res_ap.meta['fwhm'] = fwhm

    return res_ap
