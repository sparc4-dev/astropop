# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Base classes for astronomical catalogs queries."""

import copy
import numpy as np
from astropy.table import Table

from ..logger import logger
from ._online_tools import astroquery_radius, \
                           astroquery_skycoord


class _SourceCatalogClass:
    """Store and manipulate catalogs of astronomical sources."""

    _coords = None
    _ids = None
    _mags = None
    _query = None

    def __init__(self, center, radius, band=None):
        """Query the catalog and create the source catalog instance.

        Parameters
        ----------
        center: string, tuple or `astropy.coordinates.SkyCoord`
            The center of the search field.
            If center is a string, can be an object name or the string
            containing the object coordinates. If it is a tuple, have to be
            (ra, dec) coordinates, in hexa or decimal degrees format.
        radius: string, float, `~astropy.coordinates.Angle`
                or None (optional)
            The radius to search. If None, the query will be performed as
            single object query mode. Else, the query will be performed as
            field mode. If a string value is passed, it must be readable by
            astropy.coordinates.Angle. If a float value is passed, it will
            be interpreted as a decimal degree radius.
        band: string (optional)
            For catalogs with photometric information with multiple filters,
            the desired filter must be passed here.
            Default: None
        """
        self._center = astroquery_skycoord(center)
        self._radius = astroquery_radius(radius)
        if band is not None and band not in self._available_filters:
            raise ValueError(f'Filter {band} not available. Default '
                             f'filters are {self._available_filters}.')
        self._band = band

        # setup the catalog if needed
        self._setup_catalog()

        # perform the query
        logger.info('Quering region centered at %s with radius %s',
                    self._center, self._radius)
        logger.info('Using %s filter for photometry information.',
                    self._band)
        self._do_query()

    @property
    def sources_id(self):
        """Get the list of sources id in catalog."""
        return self._get_id()

    @property
    def skycoord(self):
        """Get the sources coordinates in SkyCoord format."""
        return self.get_coordinates()

    @property
    def ra_dec_list(self):
        """Get the sources coordinates in [(ra, dec)] format."""
        sk = self.skycoord
        return np.array(list(zip(sk.ra.degree, sk.dec.degree)))

    @property
    def magnitude(self):
        """Get the sources photometric mag in [(mag, mag_error)] format."""
        return np.array(list(zip(self._mags.nominal,
                                 self._mags.uncertainty)))

    @property
    def table(self):
        """Soures id, coordinates and flux information in Table format."""
        sk = self.skycoord
        fl = self.magnitude
        t = Table({'id': self.sources_id,
                   'ra': sk.ra.degree,
                   'dec': sk.dec.degree,
                   'mag': fl[:, 0],
                   'mag_error': fl[:, 1]})
        return t

    @property
    def array(self):
        """Soures id, coordinates and flux information in ndarray format."""
        return self.table.as_array()

    @property
    def center(self):
        """Center of the catalog query, in SkyCoord format."""
        return copy.copy(self._center)

    @property
    def radius(self):
        """Radius of the catalog query, in Angle format."""
        return copy.copy(self._radius)

    def copy(self):
        """Copy the current catalog to a new instance."""
        return copy.copy(self)

    def _setup_catalog(self):
        """If a catalog setup is needed."""

    def _do_query(self):
        """Query the catalog."""
        raise NotImplementedError

    def _get_id(self):
        """Get id from the queried catalog."""
        return copy.copy(self._ids)

    def get_coordinates(self, obstime=None):
        """Get the skycoord positions from the catalog."""
        try:
            return self._coords.apply_space_motion(new_obstime=obstime)
        except ValueError:
            return copy.copy(self._coords)

    def _get_mag(self):
        """Get photometric magnituce from the catalog."""
        return copy.copy(self._mags)

    def match_objects(self, ra, dec, limit_angle):
        """Match a list of ra, dec objects to this catalog.

        Parameters
        ----------
        ra, dec: float or array-like
            RA and Dec coordinates of the objects to be matched to this
            catalog. All coordinates in decimal degree format.
        limit_angle: string, float, `~astropy.coordinates.Angle`
            Angle limit for matching indexes. If string, if must be
            `~astropy.coordinates.Angle` compatible. If float, it will be
            interpreted as a decimal degree.
        """
        raise NotImplementedError

    def __getitem__(self, item):
        """Get items from the catalog.

        A new catalog with only the selected sources is returned.
        If item is a string, a column from the result query will be returned.
        """
        if isinstance(item, str):
            if self._query is None:
                raise KeyError('Empty query')
            return copy.copy(self._query[item])

        if not isinstance(item, (int, list, np.ndarray, slice, str)):
            raise KeyError(f"{item}")

        nc = copy.copy(self)
        nc._query = None
        nc._coords = self._coords[item]
        nc._ids = self._ids[item]
        if self._mags is not None:
            nc._mags = self._mags[item]
        return nc

    def __len__(self):
        return len(self.sources_id)
