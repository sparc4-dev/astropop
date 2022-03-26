# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Module to handle local (offline) astronomical catalogs."""

import abc
import numpy as np
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy import units as u

from ..astrometry.coords_utils import guess_coordinates
from .base_catalog import _BasePhotometryCatalog, match_indexes


__all__ = ['TableCatalog', 'ASCIICatalog']


class _LocalCatalog(_BasePhotometryCatalog, abc.ABC):
    type = 'local'
    id_key = None
    ra_key = None
    dec_key = None
    flux_key = None
    flux_error_key = None
    flux_unit = None
    available_filters = None
    prepend_id_key = False
    bibcode = None

    _table = None  # Where the data is stored.

    @property
    def skycoords(self):
        if self.ra_key is not None and self.dec_key is not None:
            tabs = guess_coordinates(self._table[self.ra_key],
                                     self._table[self.dec_key],
                                     skycoord=False)
            return SkyCoord(tabs[0], tabs[1], unit=('degree', 'degree'))
        return None

    @property
    def id(self):
        if self.id_key is None:
            return None
        return np.array(self._table[self.id_key])

    def _query_index(self, center=None, radius=None):
        """Query all objects within radius."""
        # If center is None, return all
        if center is None:
            return np.arange(0, len(self._table), 1)

        center = self._get_center(center)
        radius = self._get_radius(radius)
        coords = self.skycoords

        # TODO: refactor using
        sep = coords.separation(center)
        filt = np.where(sep <= radius*u.degree)
        return filt

    def query_object(self, center, radius=None):
        """Query a single object in the catalog."""
        obj = self._query_index(center, radius)
        if obj is not None:
            obj = obj[0]
        return obj

    def query_region(self, center, radius):
        """Query all objects in a region."""
        return self._query_index(center, radius)

    def match_objects(self, ra, dec, limit_angle='2 arcsec'):
        """Match objects from RA DEC list with this catalog."""
        flux_keys = ['flux', 'flux_error']
        table_props = [('id', ''), ('ra', np.nan), ('dec', np.nan),
                       ('flux', np.nan), ('flux_error', np.nan)]
        res = self._match_objects(ra, dec, None, limit_angle,
                                  flux_keys, table_props)
        return res

    def match_object_ids(self, ra, dec, limit_angle='2 arcsec'):
        return self.match_objects(ra, dec, limit_angle=limit_angle)['id']


class TableCatalog(_LocalCatalog):
    """Local catalog with any `~astropy.table.Table`compatible data."""

    type = 'local'

    def __init__(self, table, id_key=None, ra_key=None, dec_key=None,
                 flux_key=None, flux_error_key=None, flux_unit=None,
                 available_filters=None, prepend_id_key=False, bibcode=None):
        self._table = Table(table)

        self.id_key = id_key
        self.ra_key = ra_key
        self.dec_key = dec_key
        self.flux_key = flux_key
        self.flux_error_key = flux_error_key
        self.flux_unit = flux_unit
        self.available_filters = available_filters
        self.prepend_id_key = prepend_id_key
        self.bibcode = bibcode


class ASCIICatalog(TableCatalog):
    """Local catalog read from a ASCII table file."""

    def __init__(self, filename, id_key=None, ra_key=None, dec_key=None,
                 flux_key=None, flux_error_key=None, flux_unit=None,
                 available_filters=None, prepend_id_key=False, bibcode=None,
                 **reader_kwargs):
        """
        **reader_kwargs : kwargs to be passed to the Table.read function
        """
        table = Table.read(filename, **reader_kwargs)

        super().__init__(table, id_key, ra_key, dec_key, flux_key,
                         flux_error_key, flux_unit, available_filters,
                         prepend_id_key, bibcode)
