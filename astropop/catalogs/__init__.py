# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Catalog managing and query."""

from .utils import identify_stars
from .simbad import SimbadSourcesCatalog, simbad_query_id


__all__ = ['identify_stars', 'catalogs_available']


default_catalogs = {}


catalogs_available = default_catalogs.keys()
