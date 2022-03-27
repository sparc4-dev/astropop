# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Query and match objects in Vizier catalogs."""

from astropy.coordinates import SkyCoord
from astroquery.simbad import Simbad
from astropy import units as u

from ._sources_catalog import _SourceCatalogClass
from ._online_tools import _timeout_retry, astroquery_query
from ..py_utils import string_fix


__all__ = ['simbad_query_id']


def simbad_query_id(ra, dec, limit_angle, name_order=None):
    """Query name ids for a star in Simbad.

    Parameters
    ----------
    ra, dec : `float`
        RA and DEC decimal degrees coordinates to query.
    limit_angle : string, float, `~astropy.coordinates.Angle`
        Maximum radius for search.
    name_order : `list`, optional
        Order of priority of name prefixes to query.
        Default: None
    simbad : `~astroquery.simbad.Simbad`, optional
        `~astroquery.simbad.Simbad` to be used in query.

    Returns
    -------
    `str`
        The ID of the object.
    """
    if name_order is None:
        name_order = ['MAIN_ID', 'NAME', 'HD', 'HR', 'HYP', 'TYC', 'AAVSO']

    s = Simbad()

    def _strip_spaces(name):
        name = name.strip('NAME')
        name = name.strip('* ')
        # remove excessive spaces
        while '  ' in name:
            name = name.replace('  ', ' ')
        return name.strip(' ')

    q = _timeout_retry(s.query_region, SkyCoord(ra, dec,
                                                unit=(u.degree, u.degree)),
                       radius=limit_angle)

    if q is not None:
        name = string_fix(q['MAIN_ID'][0])
        ids = _timeout_retry(s.query_objectids, name)['ID']
        for i in name_order:
            if i == 'MAIN_ID':
                return _strip_spaces(name)
            for k in ids:
                if i+' ' in k:
                    return _strip_spaces(k)
    return None


class SimbadSourcesCatalog(_SourceCatalogClass):
    """Sources catalog from Simbad plataform."""

    def _setup_catalog(self):
        self._s = Simbad()
        self._s.ROW_LIMIT = 0
        if self._band is not None:
            self._s.add_votable_fields(f'fluxdata({self._band})')

    def _do_query(self):
        self._query = astroquery_query(self._s.query_region,
                                       self._center,
                                       radius=self._radius)
