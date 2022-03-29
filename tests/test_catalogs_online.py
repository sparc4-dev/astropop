# Licensed under a 3-clause BSD style license - see LICENSE.rst

import os
import time
import pytest
import numpy as np
from astropy.table import Table
from astropy.coordinates import SkyCoord, Angle
from astropop.catalogs.simbad import SimbadSourcesCatalog, simbad_query_id
from astropop.catalogs._online_tools import _timeout_retry, \
                                            _fix_query_table, \
                                            get_center_radius, \
                                            astroquery_radius, \
                                            astroquery_skycoord
from astropop.math import QFloat

from astropop.testing import assert_equal, assert_almost_equal, \
                             assert_is_instance, assert_is_none
from astroquery.simbad import Simbad


def delay_rerun(*args):
    time.sleep(10)
    return True


flaky_rerun = pytest.mark.flaky(max_runs=10, min_passes=1,
                                rerun_filter=delay_rerun)
catalog_skip = pytest.mark.skipif(not os.environ.get('ASTROPOP_TEST_CATALOGS'),
                                  reason='avoid servers errors.')

sirius_coords = ["Sirius", "06h45m09s -16d42m58s", [101.28715, -16.7161158],
                 np.array([101.28715, -16.7161158]), (101.28715, -16.7161158),
                 SkyCoord(101.28715, -16.7161158, unit=('degree', 'degree'))]
search_radius = ['0.1d', '360s', '6m', 0.1, Angle('0.1d')]


@flaky_rerun
@catalog_skip
class Test_OnlineTools:
    def test_timeout_retry_error(self):
        def _only_fail(*args, **kwargs):
            assert_equal(len(args), 1)
            assert_equal(args[0], 1)
            assert_equal(len(kwargs), 1)
            assert_equal(kwargs['test'], 2)
            raise TimeoutError

        with pytest.raises(TimeoutError, match='TimeOut obtained in'):
            _timeout_retry(_only_fail, 1, test=2)

    def test_timeout_retry_pass(self):
        i = 0

        def _only_fail(*args, **kwargs):
            nonlocal i
            assert_equal(len(args), 1)
            assert_equal(args[0], 1)
            assert_equal(len(kwargs), 1)
            assert_equal(kwargs['test'], 2)
            if i < 5:
                i += 1
                raise TimeoutError
            return i

        res = _timeout_retry(_only_fail, 1, test=2)
        assert_equal(res, 5)

    def test_wrap_table(self):
        class StrObj__:
            def __init__(self, s):
                self._s = s

            def __str__(self):
                return str(self._s)

        tab = Table()
        tab['a'] = ['A3#Â'.encode('utf-8') for i in range(10)]
        tab['b'] = ['B3#Ê' for i in range(10)]
        tab['c'] = [StrObj__(i) for i in range(10)]

        _fix_query_table(tab)

        assert_equal(len(tab), 10)
        assert_equal(tab['a'], ['A3#Â' for i in range(10)])
        assert_equal(tab['b'], ['B3#Ê' for i in range(10)])
        assert_equal(tab['c'], [f'{i}' for i in range(10)])
        assert_equal(tab['a'].dtype.char, 'U')
        assert_equal(tab['a'].dtype.char, 'U')
        assert_equal(tab['a'].dtype.char, 'U')

    def test_get_center_radius(self):
        ra = np.arange(11)
        dec = np.arange(11)
        c_ra, c_dec, rad = get_center_radius(ra, dec)
        assert_equal(c_ra, 5)
        assert_equal(c_dec, 5)
        assert_equal(rad, 10)

    @pytest.mark.parametrize('value', sirius_coords)
    def test_astroquery_skycoord_string_obj(self, value):
        skcord = astroquery_skycoord(value)
        assert_is_instance(skcord, SkyCoord)
        assert_almost_equal(skcord.ra.degree, 101.28715, decimal=3)
        assert_almost_equal(skcord.dec.degree, -16.7161158, decimal=3)

    def test_astroquery_skycoord_error(self):
        value = 'this should raise error'
        with pytest.raises(ValueError, match='could not be resolved'):
            astroquery_skycoord(value)

    def test_astroquery_radius(self):
        ang = Angle(1.0, unit='degree')
        stra = '1d'
        strb = '3600 arcsec'
        inta = 1

        assert_equal(astroquery_radius(ang), Angle("1.0d"))
        assert_equal(astroquery_radius(stra), Angle("1.0d"))
        assert_equal(astroquery_radius(strb), Angle("1.0d"))
        assert_equal(astroquery_radius(inta), Angle("1.0d"))

    def test_astroquery_radius_error(self):
        not_angle = '10 not angle'
        with pytest.raises(ValueError):
            astroquery_radius(not_angle)


@flaky_rerun
@catalog_skip
class Test_Simbad():
    def test_catalog_creation_errors(self):
        # Need arguments
        with pytest.raises(TypeError):
            SimbadSourcesCatalog()
        with pytest.raises(TypeError):
            SimbadSourcesCatalog('test')

        with pytest.raises(ValueError, match='Filter None not available.'):
            SimbadSourcesCatalog('Sirius', '0.05d', band='None')
        # Filter None should pass, no mag data
        SimbadSourcesCatalog('Sirius', '0.05d', None)

    @pytest.mark.parametrize('radius', search_radius)
    @pytest.mark.parametrize('center', sirius_coords)
    def test_catalog_creation_params(self, center, radius):
        s = SimbadSourcesCatalog(center, radius)
        assert_equal(s.sources_id[0], '* alf CMa')
        assert_almost_equal(s.ra_dec_list[0], [101.28715, -16.7161158], decimal=5)
        assert_is_none(s.magnitude)

    def test_catalog_creation_photometry(self):
        s = SimbadSourcesCatalog(sirius_coords[0],
                                 search_radius[0],
                                 band='V')
        assert_equal(s.sources_id[0], '* alf CMa')
        assert_almost_equal(s.ra_dec_list[0], [101.28715, -16.7161158], decimal=5)
        assert_almost_equal(s.mag_list[0][0], -1.46)

    def test_catalog_properties_types(self):
        s = SimbadSourcesCatalog(sirius_coords[0],
                                 search_radius[0],
                                 band='V')

        assert_is_instance(s.sources_id, np.ndarray)
        assert_equal(s.sources_id.shape, (len(s)))
        assert_is_instance(s.skycoord, SkyCoord)
        assert_is_instance(s.magnitude, QFloat)
        assert_is_instance(s.ra_dec_list, np.ndarray)
        assert_equal(s.ra_dec_list.shape, (len(s), 2))
        assert_is_instance(s.mag_list, np.ndarray)
        assert_equal(s.mag_list.shape, (len(s), 2))
        assert_is_instance(s.center, SkyCoord)
        assert_is_instance(s.radius, Angle)


class Test_SimbadQueryID:
    @pytest.mark.parametrize('order, expect', [(None, 'alf CMa'),
                                               (['NAME'], 'Dog Star'),
                                               (['*'], 'alf CMa'),
                                               (['HIP'], 'HIP 32349'),
                                               (['HIC', 'HD'], 'HIC 32349'),
                                               (['NONE', 'HD'], 'HD 48915'),
                                               (['UBV M', 'HD'],
                                                'UBV M 12413')])
    def test_simbad_query_id(self, order, expect):
        idn = simbad_query_id(101.28715, -16.7161158, '5s', name_order=order)
        assert_equal(idn, expect)

    @pytest.mark.parametrize('coords,name', [((16.82590917, -72.4676825),
                                              'HD 6884'),
                                             ((86.46641167, -67.24053806),
                                              'LHA 120-S 61')])
    def test_simbad_query_id_non_default(self, coords, name):
        order = ['NAME', 'HD', 'HR', 'HYP', 'AAVSO', 'LHA']
        idn = simbad_query_id(*coords, '5s', name_order=order)
        assert_equal(idn, name)
