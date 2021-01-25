# Licensed under a 3-clause BSD style license - see LICENSE.rst

import numpy as np
import pytest
from astropop.math.physical import QFloat, UnitsError, units
from numpy.testing import assert_almost_equal, assert_equal
from packaging import version

# Testing qfloat compatibility with Numpy ufuncs and array functions.


class TestQFloatNumpyArrayFuncs:
    """Test numpy array functions for numpy comatibility."""

    def test_qfloat_np_append(self):
        qf1 = QFloat([1.0, 2.0, 3.0], [0.1, 0.2, 0.3], unit="m")
        qf2 = QFloat([1.0], [0.1], unit="km")
        qf3 = QFloat(1.0, 0.1, unit="km")
        qf4 = QFloat(0, 0)

        qf = np.append(qf1, qf1)
        assert_equal(qf.nominal, [1.0, 2.0, 3.0, 1.0, 2.0, 3.0])
        assert_equal(qf.std_dev, [0.1, 0.2, 0.3, 0.1, 0.2, 0.3])
        assert_equal(qf.unit, qf1.unit)

        # This should work and convert the unit.
        qf = np.append(qf1, qf2)
        assert_equal(qf.nominal, [1.0, 2.0, 3.0, 1000.0])
        assert_equal(qf.std_dev, [0.1, 0.2, 0.3, 100.0])
        assert_equal(qf.unit, qf1.unit)

        # Also this should work and convert the unit in the same way.
        qf = np.append(qf1, qf3)
        assert_equal(qf.nominal, [1.0, 2.0, 3.0, 1000.0])
        assert_equal(qf.std_dev, [0.1, 0.2, 0.3, 100.0])
        assert_equal(qf.unit, qf1.unit)

        # This should fail due to unit
        with pytest.raises(UnitsError):
            qf = np.append(qf1, qf4)

        # Testing with axis
        qf1 = QFloat([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
                     [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]], "m",)
        qf = np.append(qf1, QFloat([[8.0], [9.0]], [[0.8], [0.9]], "m"),
                       axis=1)
        assert_equal(qf.nominal, [[1.0, 2.0, 3.0, 8.0], [4.0, 5.0, 6.0, 9.0]])
        assert_equal(qf.std_dev, [[0.1, 0.2, 0.3, 0.8], [0.4, 0.5, 0.6, 0.9]])
        qf = np.append(qf1, QFloat([[7.0, 8.0, 9.0]], [[0.7, 0.8, 0.9]], "m"),
                       axis=0)
        assert_equal(qf.nominal, [[1.0, 2.0, 3.0],
                                  [4.0, 5.0, 6.0],
                                  [7.0, 8.0, 9.0]])
        assert_equal(qf.std_dev, [[0.1, 0.2, 0.3],
                                  [0.4, 0.5, 0.6],
                                  [0.7, 0.8, 0.9]])

    def test_qfloat_np_around(self):
        # single case
        qf = np.around(QFloat(1.02549, 0.135964))
        assert_equal(qf.nominal, 1)
        assert_equal(qf.std_dev, 0)

        qf = np.around(QFloat(1.02549, 0.135964), decimals=2)
        assert_equal(qf.nominal, 1.03)
        assert_equal(qf.std_dev, 0.14)

        # just check array too
        qf = np.around(QFloat([1.03256, 2.108645], [0.01456, 0.594324]),
                       decimals=2)
        assert_equal(qf.nominal, [1.03, 2.11])
        assert_equal(qf.std_dev, [0.01, 0.59])

    def test_qfloat_np_atleast_1d(self):
        # This function is not implemented, so should raise
        with pytest.raises(TypeError):
            np.atleast_1d(QFloat([1.0, 2.0], [0.1, 0.2], "m"))

    def test_qfloat_np_atleast_2d(self):
        # This function is not implemented, so should raise
        with pytest.raises(TypeError):
            np.atleast_2d(QFloat([1.0, 2.0], [0.1, 0.2], "m"))

    def test_qfloat_np_atleast_3d(self):
        # This function is not implemented, so should raise
        with pytest.raises(TypeError):
            np.atleast_3d(QFloat([1.0, 2.0], [0.1, 0.2], "m"))

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_broadcast(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_broadcast_to(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_ceil(self):
        raise NotImplementedError

    def test_qfloat_np_clip(self):
        arr = np.arange(10)
        qf = QFloat(arr, arr * 0.1, "m")

        res = np.clip(qf, 2, 8)
        tgt = [2, 2, 2, 3, 4, 5, 6, 7, 8, 8]
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, arr * 0.1)
        assert_equal(qf.unit, res.unit)

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_columnstack(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_concatenate(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_copyto(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_cross(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_cumprod(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_cumsum(self):
        raise NotImplementedError

    def test_qfloat_np_delete(self):
        a = np.array([[1.0, 2.0, 3.0, 4.0],
                      [5.0, 6.0, 7.0, 8.0],
                      [9.0, 10.0, 11.0, 12.0]]        )
        qf = QFloat(a, a * 0.1, "m")
        res1 = np.delete(qf, 1, axis=0)
        assert_almost_equal(res1.nominal, [[1.0, 2.0, 3.0, 4.0],
                                           [9.0, 10.0, 11.0, 12.0]])
        assert_almost_equal(res1.std_dev, [[0.1, 0.2, 0.3, 0.4],
                                           [0.9, 1.0, 1.1, 1.2]])
        assert_equal(res1.unit, qf.unit)

        res2 = np.delete(qf, 1, axis=1)
        assert_almost_equal(res2.nominal, [[1.0, 3.0, 4.0],
                                           [5.0, 7.0, 8.0],
                                           [9.0, 11.0, 12.0]])
        assert_almost_equal(res2.std_dev, [[0.1, 0.3, 0.4],
                                           [0.5, 0.7, 0.8],
                                           [0.9, 1.1, 1.2]])
        assert_equal(res2.unit, qf.unit)

        res3 = np.delete(qf, np.s_[::2], 1)
        assert_almost_equal(res3.nominal,
                            [[2.0, 4.0], [6.0, 8.0], [10.0, 12.0]])
        assert_almost_equal(res3.std_dev,
                            [[0.2, 0.4], [0.6, 0.8], [1.0, 1.2]])
        assert_equal(res3.unit, qf.unit)

        res4 = np.delete(qf, [1, 3, 5])
        assert_almost_equal(res4.nominal,
                            [1.0, 3.0, 5.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0])
        assert_almost_equal(res4.std_dev,
                            [0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2])
        assert_equal(res4.unit, qf.unit)

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_diff(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_dstack(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_ediff1d(self):
        raise NotImplementedError

    def test_qfloat_np_expand_dims(self):
        qf = QFloat(1.0, 0.1, "m")
        res1 = np.expand_dims(qf, axis=0)
        assert_almost_equal(res1.nominal, [1.0])
        assert_almost_equal(res1.std_dev, [0.1])
        assert_equal(res1.unit, qf.unit)
        assert_equal(res1.shape, (1,))

        qf = QFloat([1.0, 2.0], [0.1, 0.2], "m")
        res2 = np.expand_dims(qf, axis=0)
        assert_almost_equal(res2.nominal, [[1.0, 2.0]])
        assert_almost_equal(res2.std_dev, [[0.1, 0.2]])
        assert_equal(res2.unit, qf.unit)
        assert_equal(res2.shape, (1, 2))
        res3 = np.expand_dims(qf, axis=1)
        assert_almost_equal(res3.nominal, [[1.0], [2.0]])
        assert_almost_equal(res3.std_dev, [[0.1], [0.2]])
        assert_equal(res3.unit, qf.unit)
        assert_equal(res3.shape, (2, 1))

        if version.parse(np.version.full_version) >= version.parse('1.18.0'):
            res4 = np.expand_dims(qf, axis=(2, 0))
            assert_almost_equal(res4.nominal, [[[1.0], [2.0]]])
            assert_almost_equal(res4.std_dev, [[[0.1], [0.2]]])
            assert_equal(res4.unit, qf.unit)
            assert_equal(res4.shape, (1, 2, 1))

    def test_qfloat_np_flip(self):
        a = np.arange(8).reshape((2, 2, 2))
        qf = QFloat(a, a * 0.1, "m")

        res1 = np.flip(qf)
        assert_equal(res1.nominal, a[::-1, ::-1, ::-1])
        assert_equal(res1.std_dev, a[::-1, ::-1, ::-1] * 0.1)
        assert_equal(res1.unit, qf.unit)

        res2 = np.flip(qf, 0)
        assert_equal(res2.nominal, a[::-1, :, :])
        assert_equal(res2.std_dev, a[::-1, :, :] * 0.1)
        assert_equal(res2.unit, qf.unit)

        res3 = np.flip(qf, 1)
        assert_equal(res3.nominal, a[:, ::-1, :])
        assert_equal(res3.std_dev, a[:, ::-1, :] * 0.1)
        assert_equal(res3.unit, qf.unit)

        res4 = np.flip(qf, 2)
        assert_equal(res4.nominal, a[:, :, ::-1])
        assert_equal(res4.std_dev, a[:, :, ::-1] * 0.1)
        assert_equal(res4.unit, qf.unit)

        # just some static check
        qf = QFloat([[1, 2], [3, 4]], [[0.1, 0.2], [0.3, 0.4]], "m")

        res5 = np.flip(qf)
        assert_equal(res5.nominal, [[4, 3], [2, 1]])
        assert_equal(res5.std_dev, [[0.4, 0.3], [0.2, 0.1]])
        assert_equal(res5.unit, qf.unit)

        res6 = np.flip(qf, 0)
        assert_equal(res6.nominal, [[3, 4], [1, 2]])
        assert_equal(res6.std_dev, [[0.3, 0.4], [0.1, 0.2]])
        assert_equal(res6.unit, qf.unit)

        res7 = np.flip(qf, 1)
        assert_equal(res7.nominal, [[2, 1], [4, 3]])
        assert_equal(res7.std_dev, [[0.2, 0.1], [0.4, 0.3]])
        assert_equal(res7.unit, qf.unit)

    def test_qfloat_np_fliplr(self):
        a = np.arange(8).reshape((2, 2, 2))
        qf = QFloat(a, a * 0.1, "m")
        res = np.fliplr(qf)
        assert_equal(res.nominal, a[:, ::-1, :])
        assert_equal(res.std_dev, a[:, ::-1, :] * 0.1)
        assert_equal(res.unit, qf.unit)

        qf = QFloat([[1, 2], [3, 4]], [[0.1, 0.2], [0.3, 0.4]], "m")
        res = np.fliplr(qf)
        assert_equal(res.nominal, [[2, 1], [4, 3]])
        assert_equal(res.std_dev, [[0.2, 0.1], [0.4, 0.3]])
        assert_equal(res.unit, qf.unit)

    def test_qfloat_np_flipud(self):
        a = np.arange(8).reshape((2, 2, 2))
        qf = QFloat(a, a * 0.1, "m")
        res = np.flipud(qf)
        assert_equal(res.nominal, a[::-1, :, :])
        assert_equal(res.std_dev, a[::-1, :, :] * 0.1)
        assert_equal(res.unit, qf.unit)

        qf = QFloat([[1, 2], [3, 4]], [[0.1, 0.2], [0.3, 0.4]], "m")
        res = np.flipud(qf)
        assert_equal(res.nominal, [[3, 4], [1, 2]])
        assert_equal(res.std_dev, [[0.3, 0.4], [0.1, 0.2]])
        assert_equal(res.unit, qf.unit)

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_hstack(self):
        raise NotImplementedError

    def test_qfloat_np_insert(self):
        a = np.array([[1, 2], [3, 4], [5, 6]])
        qf = QFloat(a, a * 0.1, "m")

        res = np.insert(qf, 5, QFloat(999, 0.1, unit="m"))
        assert_almost_equal(res.nominal, [1, 2, 3, 4, 5, 999, 6])
        assert_almost_equal(res.std_dev, [0.1, 0.2, 0.3, 0.4, 0.5, 0.1, 0.6])
        assert_equal(res.unit, qf.unit)

        res = np.insert(qf, 1, QFloat(999, 0.1, unit="m"), axis=1)
        assert_almost_equal(res.nominal,
                            [[1, 999, 2], [3, 999, 4], [5, 999, 6]])
        assert_almost_equal(res.std_dev, [[0.1, 0.1, 0.2],
                                          [0.3, 0.1, 0.4],
                                          [0.5, 0.1, 0.6]])
        assert_equal(res.unit, qf.unit)

    def test_qfloat_np_moveaxis(self):
        arr = np.zeros((3, 4, 5))
        qf = QFloat(arr, unit='m')

        res = np.moveaxis(qf, 0, -1)
        assert_equal(res.shape, (4, 5, 3))
        assert_equal(res.unit, qf.unit)

        res = np.moveaxis(qf, -1, 0)
        assert_equal(res.shape, (5, 3, 4))
        assert_equal(res.unit, qf.unit)

        res = np.moveaxis(qf, (0, 1), (-1, -2))
        assert_equal(res.shape, (5, 4, 3))
        assert_equal(res.unit, qf.unit)

        res = np.moveaxis(qf, [0, 1, 2], [-1, -2, -3])
        assert_equal(res.shape, (5, 4, 3))
        assert_equal(res.unit, qf.unit)

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_nancumprod(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_nancumsum(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_nanprod(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_nansum(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_prod(self):
        raise NotImplementedError

    def test_qfloat_np_ravel(self):
        arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
        tgt = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        qf = QFloat(arr, arr * 0.1, "m")

        res = np.ravel(qf)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)

    def test_qfloat_np_repeat(self):
        arr = np.array([1, 2, 3])
        tgt = np.array([1, 1, 2, 2, 3, 3])
        qf = QFloat(arr, arr * 0.1, "m")

        res = np.repeat(qf, 2)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)

    def test_qfloat_np_reshape(self):
        arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
        tgt = np.array([[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]])
        qf = QFloat(arr, arr * 0.1, "m")

        res = np.reshape(qf, (2, 6))
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)
        assert_equal(res.shape, (2, 6))

    def test_qfloat_np_resize(self):
        arr = np.array([[1, 2], [3, 4]])
        qf = QFloat(arr, arr * 0.1, "m")

        shp = (2, 4)
        tgt = np.array([[1, 2, 3, 4], [1, 2, 3, 4]])
        res = np.resize(qf, shp)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)
        assert_equal(res.shape, shp)

        shp = (4, 2)
        tgt = np.array([[1, 2], [3, 4], [1, 2], [3, 4]])
        res = np.resize(qf, shp)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)
        assert_equal(res.shape, shp)

        shp = (4, 3)
        tgt = np.array([[1, 2, 3], [4, 1, 2], [3, 4, 1], [2, 3, 4]])
        res = np.resize(qf, shp)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)
        assert_equal(res.shape, shp)

        shp = (0,)
        tgt = np.array([])
        res = np.resize(qf, shp)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)
        assert_equal(res.shape, shp)

    def test_qfloat_np_roll(self):
        arr = np.arange(10)
        qf = QFloat(arr, arr * 0.01, "m")

        off = 2
        tgt = np.array([8, 9, 0, 1, 2, 3, 4, 5, 6, 7])
        res = np.roll(qf, off)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.01)
        assert_equal(res.unit, qf.unit)

        off = -2
        tgt = np.array([2, 3, 4, 5, 6, 7, 8, 9, 0, 1])
        res = np.roll(qf, off)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.01)
        assert_equal(res.unit, qf.unit)

        arr = np.arange(12).reshape((4, 3))
        qf = QFloat(arr, arr * 0.01, "m")

        ax = 0
        off = 1
        tgt = np.array([[9, 10, 11], [0, 1, 2], [3, 4, 5], [6, 7, 8]])
        res = np.roll(qf, off, axis=ax)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.01)
        assert_equal(res.unit, qf.unit)

        ax = 1
        off = 1
        tgt = np.array([[2, 0, 1], [5, 3, 4], [8, 6, 7], [11, 9, 10]])
        res = np.roll(qf, off, axis=ax)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.01)
        assert_equal(res.unit, qf.unit)

    def test_qfloat_np_rollaxis(self):
        arr = np.ones((3, 4, 5, 6))
        qf = QFloat(arr, arr * 0.01, "m")

        res = np.rollaxis(qf, 3, 1)
        assert_equal(res.shape, (3, 6, 4, 5))

        res = np.rollaxis(qf, 2)
        assert_equal(res.shape, (5, 3, 4, 6))

        res = np.rollaxis(qf, 1, 4)
        assert_equal(res.shape, (3, 5, 6, 4))

    def test_qfloat_np_round(self):
        # single case
        qf = np.round(QFloat(1.02549, 0.135964))
        assert_equal(qf.nominal, 1)
        assert_equal(qf.std_dev, 0)

        qf = np.round(QFloat(1.02549, 0.135964), decimals=2)
        assert_equal(qf.nominal, 1.03)
        assert_equal(qf.std_dev, 0.14)

        # just check array too
        qf = np.round(QFloat([1.03256, 2.108645], [0.01456, 0.594324]),
                             decimals=2)
        assert_equal(qf.nominal, [1.03, 2.11])
        assert_equal(qf.std_dev, [0.01, 0.59])

    def test_qfloat_np_rot90(self):
        arr = np.array([[0, 1, 2], [3, 4, 5]])
        b1 = np.array([[2, 5], [1, 4], [0, 3]])
        b2 = np.array([[5, 4, 3], [2, 1, 0]])
        b3 = np.array([[3, 0], [4, 1], [5, 2]])
        b4 = np.array([[0, 1, 2], [3, 4, 5]])
        qf = QFloat(arr, arr * 0.1, "m")

        for k in range(-3, 13, 4):
            res = np.rot90(qf, k=k)
            assert_equal(res.nominal, b1)
            assert_equal(res.std_dev, b1 * 0.1)
            assert_equal(res.unit, qf.unit)
        for k in range(-2, 13, 4):
            res = np.rot90(qf, k=k)
            assert_equal(res.nominal, b2)
            assert_equal(res.std_dev, b2 * 0.1)
            assert_equal(res.unit, qf.unit)
        for k in range(-1, 13, 4):
            res = np.rot90(qf, k=k)
            assert_equal(res.nominal, b3)
            assert_equal(res.std_dev, b3 * 0.1)
            assert_equal(res.unit, qf.unit)
        for k in range(0, 13, 4):
            res = np.rot90(qf, k=k)
            assert_equal(res.nominal, b4)
            assert_equal(res.std_dev, b4 * 0.1)
            assert_equal(res.unit, qf.unit)

        arr = np.arange(8).reshape((2, 2, 2))
        qf = QFloat(arr, arr * 0.1, "m")

        ax = (0, 1)
        tgt = np.array([[[2, 3], [6, 7]], [[0, 1], [4, 5]]])
        res = np.rot90(qf, axes=ax)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)

        ax = (1, 2)
        tgt = np.array([[[1, 3], [0, 2]], [[5, 7], [4, 6]]])
        res = np.rot90(qf, axes=ax)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)

        ax = (2, 0)
        tgt = np.array([[[4, 0], [6, 2]], [[5, 1], [7, 3]]])
        res = np.rot90(qf, axes=ax)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)

        ax = (1, 0)
        tgt = np.array([[[4, 5], [0, 1]], [[6, 7], [2, 3]]])
        res = np.rot90(qf, axes=ax)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)

    def test_qfloat_np_shape(self):
        for shp in [(10,), (11, 12), (11, 12, 13)]:
            qf = QFloat(np.ones(shp), np.ones(shp), "m")
            assert_equal(np.shape(qf), shp)

    def test_qfloat_np_size(self):
        for shp in [(10,), (11, 12), (11, 12, 13)]:
            qf = QFloat(np.ones(shp), np.ones(shp), "m")
            assert_equal(np.size(qf), np.prod(shp))

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_square(self):
        raise NotImplementedError

    def test_qfloat_np_squeeze(self):
        arr = np.array([[[0], [1], [2]]])
        qf = QFloat(arr, arr * 0.01, "m")

        res = np.squeeze(qf)
        assert_equal(res.shape, (3,))
        assert_almost_equal(res.nominal, [0, 1, 2])
        assert_almost_equal(res.std_dev, [0, 0.01, 0.02])
        assert_equal(res.unit, qf.unit)

        res = np.squeeze(qf, axis=0)
        assert_equal(res.shape, (3, 1))
        assert_almost_equal(res.nominal, [[0], [1], [2]])
        assert_almost_equal(res.std_dev, [[0], [0.01], [0.02]])
        assert_equal(res.unit, qf.unit)

        with pytest.raises(ValueError):
            np.squeeze(qf, axis=1)

        res = np.squeeze(qf, axis=2)
        assert_equal(res.shape, (1, 3))
        assert_almost_equal(res.nominal, [[0, 1, 2]])
        assert_almost_equal(res.std_dev, [[0, 0.01, 0.02]])
        assert_equal(res.unit, qf.unit)

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_sum(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_stack(self):
        raise NotImplementedError

    def test_qfloat_np_swapaxes(self):
        arr = np.array([[[0, 1], [2, 3]], [[4, 5], [6, 7]]])
        tgt = np.array([[[0, 4], [2, 6]], [[1, 5], [3, 7]]])
        qf = QFloat(arr, arr * 0.1, "m")

        res = np.swapaxes(qf, 0, 2)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)

    def test_qfloat_np_take(self):
        arr = np.array([1, 2, 3, 4, 5])
        tgt = np.array([2, 3, 5])
        ind = [1, 2, 4]
        qf = QFloat(arr, arr * 0.1, "m")

        res = np.take(qf, ind)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)

    def test_qfloat_np_tile(self):
        arr = np.array([0, 1, 2])
        qf = QFloat(arr, arr * 0.1)

        tile = 2
        tgt = np.array([0, 1, 2, 0, 1, 2])
        res = np.tile(qf, tile)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)

        tile = (2, 2)
        tgt = np.array([[0, 1, 2, 0, 1, 2], [0, 1, 2, 0, 1, 2]])
        res = np.tile(qf, tile)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)

        # More checking
        arr = np.array([[1, 2], [3, 4]])
        qf = QFloat(arr, arr * 0.1)

        tile = 2
        tgt = np.array([[1, 2, 1, 2], [3, 4, 3, 4]])
        res = np.tile(qf, tile)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)

        tile = (2, 1)
        tgt = np.array([[1, 2], [3, 4], [1, 2], [3, 4]])
        res = np.tile(qf, tile)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)

    def test_qfloat_np_transpose(self):
        arr = np.array([[1, 2], [3, 4], [5, 6]])
        tgt = np.array([[1, 3, 5], [2, 4, 6]])
        qf = QFloat(arr, arr * 0.1, "m")

        res = np.transpose(qf)
        assert_almost_equal(res.nominal, tgt)
        assert_almost_equal(res.std_dev, tgt * 0.1)
        assert_equal(res.unit, qf.unit)

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_trunc(self):
        raise NotImplementedError


class TestQFloatNumpyUfuncs:
    """Test numpy array functions for numpy comatibility."""

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_absolute(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_add(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_cbrt(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_ceil(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_copysign(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_divide(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_divmod(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_exp(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_exp2(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_expm1(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_fabs(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_float_power(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_floor(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_floor_divide(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_fmax(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_fmin(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_fmod(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_hypot(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_isfinit(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_isinf(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_isnan(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_log(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_log2(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_log10(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_log1p(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_maximum(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_minimum(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_mod(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_modf(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_multiply(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_negative(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_positive(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_power(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_remainder(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_rint(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_sign(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_signbit(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_sqrt(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_squared(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_subtract(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_true_divide(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not Implemented Yet")
    def test_qfloat_np_trunc(self):
        raise NotImplementedError


class TestQFloatNumpyUfuncTrigonometric:
    """Test the numpy trigonometric and inverse trigonometric functions."""

    # Both radians and deg2rad must work in the same way
    @pytest.mark.parametrize('func', [np.radians, np.deg2rad])
    def test_qfloat_np_radians(self, func):
        qf = QFloat(180, 0.1, 'degree')
        res = func(qf)
        assert_almost_equal(res.nominal, 3.141592653589793)
        assert_almost_equal(res.std_dev, 0.001745329251994)
        assert_equal(res.unit, units.Unit('rad'))

        qf = QFloat(-180, 0.1, 'degree')
        res = func(qf)
        assert_almost_equal(res.nominal, -3.141592653589793)
        assert_almost_equal(res.std_dev, 0.001745329251994)
        assert_equal(res.unit, units.Unit('rad'))

        qf = QFloat([0, 30, 45, 60, 90], [0.1, 0.2, 0.3, 0.4, 0.5], 'degree')
        res = func(qf)
        assert_almost_equal(res.nominal, [0, 0.52359878, 0.78539816,
                                          1.04719755, 1.57079633])
        assert_almost_equal(res.std_dev, [0.00174533, 0.00349066, 0.00523599,
                                          0.00698132, 0.00872665])
        assert_equal(res.unit, units.Unit('rad'))

        # radian should no change
        qf = QFloat(1.0, 0.1, 'radian')
        res = func(qf)
        assert_equal(res.nominal, 1.0)
        assert_equal(res.std_dev, 0.1)
        assert_equal(res.unit, units.Unit('rad'))

        # Invalid units
        for unit in ('m', None, 'm/s'):
            with pytest.raises(UnitsError):
                func(QFloat(1.0, 0.1, unit))

    # Both degrees and rad2deg must work in the same way
    @pytest.mark.parametrize('func', [np.degrees, np.rad2deg])
    def test_qfloat_np_degrees(self, func):
        qf = QFloat(np.pi, 0.05, 'radian')
        res = func(qf)
        assert_almost_equal(res.nominal, 180.0)
        assert_almost_equal(res.std_dev, 2.8647889756541165)
        assert_equal(res.unit, units.Unit('deg'))

        qf = QFloat(-np.pi, 0.05, 'radian')
        res = func(qf)
        assert_almost_equal(res.nominal, -180.0)
        assert_almost_equal(res.std_dev, 2.8647889756541165)
        assert_equal(res.unit, units.Unit('deg'))

        qf = QFloat([np.pi, np.pi/2, np.pi/4, np.pi/6],
                    [0.01, 0.02, 0.03, 0.04], 'rad')
        res = func(qf)
        assert_almost_equal(res.nominal, [180.0, 90.0, 45.0, 30.0])
        assert_almost_equal(res.std_dev, [0.5729578 , 1.14591559,
                                          1.71887339, 2.29183118])
        assert_equal(res.unit, units.Unit('deg'))

        # deg should no change
        qf = QFloat(1.0, 0.1, 'deg')
        res = func(qf)
        assert_equal(res.nominal, 1.0)
        assert_equal(res.std_dev, 0.1)
        assert_equal(res.unit, units.Unit('deg'))

        # Invalid units
        for unit in ('m', None, 'm/s'):
            with pytest.raises(UnitsError):
                func(QFloat(1.0, 0.1, unit))

    def test_qfloat_np_sin(self):
        qf = QFloat(np.pi, 0.05, 'radian')
        res = np.sin(qf)
        assert_almost_equal(res.nominal, 0.0)
        assert_almost_equal(res.std_dev, 0.05)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat(90, 0.05, 'deg')
        res = np.sin(qf)
        assert_almost_equal(res.nominal, 1.0)
        assert_almost_equal(res.std_dev, 0.0)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat([30, 45, 60], [0.1, 0.2, 0.3], 'deg')
        res = np.sin(qf)
        assert_almost_equal(res.nominal, [0.5, 0.70710678, 0.8660254])
        assert_almost_equal(res.std_dev, [0.0015115, 0.00246827, 0.00261799])
        assert_equal(res.unit, units.dimensionless_unscaled)

        for unit in ['m', 'm/s', None]:
            with pytest.raises(UnitsError):
                np.sin(QFloat(1.0, unit=unit))

    def test_qfloat_np_cos(self):
        qf = QFloat(180, 0.05, 'deg')
        res = np.cos(qf)
        assert_almost_equal(res.nominal, -1.0)
        assert_almost_equal(res.std_dev, 0.0)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat(np.pi/2, 0.05, 'rad')
        res = np.cos(qf)
        assert_almost_equal(res.nominal, 0.0)
        assert_almost_equal(res.std_dev, 0.05)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat([30, 45, 60], [0.1, 0.2, 0.3], 'deg')
        res = np.cos(qf)
        assert_almost_equal(res.nominal, [0.8660254, 0.70710678, 0.5])
        assert_almost_equal(res.std_dev, [0.00087266, 0.00246827, 0.0045345])
        assert_equal(res.unit, units.dimensionless_unscaled)

        for unit in ['m', 'm/s', None]:
            with pytest.raises(UnitsError):
                np.cos(QFloat(1.0, unit=unit))

    def test_qfloat_np_tan(self):
        qf = QFloat(45, 0.05, 'deg')
        res = np.tan(qf)
        assert_almost_equal(res.nominal, 1.0)
        assert_almost_equal(res.std_dev, 0.0017453292519943294)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat(np.pi/4, 0.05, 'rad')
        res = np.tan(qf)
        assert_almost_equal(res.nominal, 1.0)
        assert_almost_equal(res.std_dev, 0.1)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat([0, 30, 60], [0.1, 0.2, 0.3], 'deg')
        res = np.tan(qf)
        assert_almost_equal(res.nominal, [0, 0.57735027, 1.73205081])
        assert_almost_equal(res.std_dev, [0.00174533, 0.00465421, 0.02094395])
        assert_equal(res.unit, units.dimensionless_unscaled)

        for unit in ['m', 'm/s', None]:
            with pytest.raises(UnitsError):
                np.tan(QFloat(1.0, unit=unit))

    def test_qfloat_np_sinh(self):
        qf = QFloat(0, 0.05, 'radian')
        res = np.sinh(qf)
        assert_almost_equal(res.nominal, 0.0)
        assert_almost_equal(res.std_dev, 0.05)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat(np.pi, 0.05, 'radian')
        res = np.sinh(qf)
        assert_almost_equal(res.nominal, 11.548739357257748)
        assert_almost_equal(res.std_dev, 0.5795976637760759)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat(90, 0.05, 'deg')
        res = np.sinh(qf)
        assert_almost_equal(res.nominal, 2.3012989023072947)
        assert_almost_equal(res.std_dev, 0.002189671298638268)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat([30, 45, 60], [0.1, 0.2, 0.3], 'deg')
        res = np.sinh(qf)
        assert_almost_equal(res.nominal, [0.5478535, 0.86867096, 1.24936705])
        assert_almost_equal(res.std_dev, [0.0019901, 0.0046238, 0.0083791])
        assert_equal(res.unit, units.dimensionless_unscaled)

        for unit in ['m', 'm/s', None]:
            with pytest.raises(UnitsError):
                np.sinh(QFloat(1.0, unit=unit))

    def test_qfloat_np_cosh(self):
        qf = QFloat(0, 0.05, 'radian')
        res = np.cosh(qf)
        assert_almost_equal(res.nominal, 1.0)
        assert_almost_equal(res.std_dev, 0.0)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat(np.pi, 0.05, 'radian')
        res = np.cosh(qf)
        assert_almost_equal(res.nominal, 11.591953275521519)
        assert_almost_equal(res.std_dev, 0.5774369678628875)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat(90, 0.05, 'deg')
        res = np.cosh(qf)
        assert_almost_equal(res.nominal, 2.5091784786580567)
        assert_almost_equal(res.std_dev, 0.0020082621458896)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat([30, 45, 60], [0.1, 0.2, 0.3], 'deg')
        res = np.cosh(qf)
        assert_almost_equal(res.nominal, [1.14023832, 1.32460909, 1.60028686])
        assert_almost_equal(res.std_dev, [0.00095618, 0.00303223, 0.00654167])
        assert_equal(res.unit, units.dimensionless_unscaled)

        for unit in ['m', 'm/s', None]:
            with pytest.raises(UnitsError):
                np.cosh(QFloat(1.0, unit=unit))

    def test_qfloat_np_tanh(self):
        qf = QFloat(0, 0.05, 'radian')
        res = np.tanh(qf)
        assert_almost_equal(res.nominal, 0.0)
        assert_almost_equal(res.std_dev, 0.05)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat(np.pi, 0.05, 'radian')
        res = np.tanh(qf)
        assert_almost_equal(res.nominal, 0.99627207622075)
        assert_almost_equal(res.std_dev, 0.00037209750714)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat(90, 0.05, 'deg')
        res = np.tanh(qf)
        assert_almost_equal(res.nominal, 0.9171523356672744)
        assert_almost_equal(res.std_dev, 0.0001386067128590)
        assert_equal(res.unit, units.dimensionless_unscaled)

        qf = QFloat([30, 45, 60], [0.1, 0.2, 0.3], 'deg')
        res = np.tanh(qf)
        assert_almost_equal(res.nominal, [0.48047278, 0.6557942, 0.78071444])
        assert_almost_equal(res.std_dev, [0.00134241, 0.00198944, 0.00204457])
        assert_equal(res.unit, units.dimensionless_unscaled)

        for unit in ['m', 'm/s', None]:
            with pytest.raises(UnitsError):
                np.tanh(QFloat(1.0, unit=unit))

    def test_qfloat_np_arcsin(self):
        qf = QFloat(np.sqrt(2)/2, 0.01)
        res = np.arcsin(qf)
        assert_almost_equal(res.nominal, 0.7853981633974484)
        assert_almost_equal(res.std_dev, 0.0141421356237309)
        assert_equal(res.unit, units.Unit('rad'))

        qf = QFloat([0, 0.5, 1], [0.01, 0.2, 0.3])
        res = np.arcsin(qf)
        assert_almost_equal(res.nominal, [0, 0.52359878, 1.57079633])
        assert_almost_equal(res.std_dev, [0.01, 0.23094011, np.inf])
        assert_equal(res.unit, units.Unit('rad'))

        # Invalid units
        for unit in ['m', 'm/s', 'rad', 'deg']:
            with pytest.raises(UnitsError):
                np.arcsin(QFloat(1.0, unit=unit))

    def test_qfloat_np_arccos(self):
        qf = QFloat(np.sqrt(2)/2, 0.01)
        res = np.arccos(qf)
        assert_almost_equal(res.nominal, 0.7853981633974484)
        assert_almost_equal(res.std_dev, 0.0141421356237309)
        assert_equal(res.unit, units.Unit('rad'))

        qf = QFloat([0, 0.5, 1], [0.01, 0.2, 0.3])
        res = np.arccos(qf)
        assert_almost_equal(res.nominal, [1.57079633, 1.04719755, 0])
        assert_almost_equal(res.std_dev, [0.01, 0.23094011, np.inf])
        assert_equal(res.unit, units.Unit('rad'))

        # Invalid units
        for unit in ['m', 'm/s', 'rad', 'deg']:
            with pytest.raises(UnitsError):
                np.arccos(QFloat(1.0, unit=unit))

    def test_qfloat_np_arctan(self):
        qf = QFloat(1.0, 0.01)
        res = np.arctan(qf)
        assert_almost_equal(res.nominal, 0.7853981633974484)
        assert_almost_equal(res.std_dev, 0.005)
        assert_equal(res.unit, units.Unit('rad'))

        qf = QFloat([0, 0.5, 1], [0.01, 0.2, 0.3])
        res = np.arctan(qf)
        assert_almost_equal(res.nominal, [0, 0.4636476, 0.7853982])
        assert_almost_equal(res.std_dev, [0.01, 0.16, 0.15])
        assert_equal(res.unit, units.Unit('rad'))

        # Invalid units
        for unit in ['m', 'm/s', 'rad', 'deg']:
            with pytest.raises(UnitsError):
                np.arctan(QFloat(1.0, unit=unit))

    def test_qfloat_np_arcsinh(self):
        qf = QFloat(0.0, 0.01)
        res = np.arcsinh(qf)
        assert_almost_equal(res.nominal, 0.0)
        assert_almost_equal(res.std_dev, 0.01)
        assert_equal(res.unit, units.Unit('rad'))

        qf = QFloat([0.5, 1.0, 10], [0.01, 0.2, 0.3])
        res = np.arcsinh(qf)
        assert_almost_equal(res.nominal, [0.4812118, 0.8813736, 2.998223])
        assert_almost_equal(res.std_dev, [0.0089443, 0.1414214, 0.0298511])
        assert_equal(res.unit, units.Unit('rad'))

        # Invalid units
        for unit in ['m', 'm/s', 'rad', 'deg']:
            with pytest.raises(UnitsError):
                np.arcsinh(QFloat(1.0, unit=unit))

    def test_qfloat_np_arccosh(self):
        qf = QFloat(1.0, 0.01)
        res = np.arccosh(qf)
        assert_almost_equal(res.nominal, 0.0)
        assert_almost_equal(res.std_dev, np.inf)
        assert_equal(res.unit, units.Unit('rad'))

        qf = QFloat([1.5, 5.0, 10], [0.01, 0.2, 0.3])
        res = np.arccosh(qf)
        assert_almost_equal(res.nominal, [0.9624237, 2.2924317, 2.9932228])
        assert_almost_equal(res.std_dev, [0.0089443, 0.0408248, 0.0301511])
        assert_equal(res.unit, units.Unit('rad'))

        # Invalid units
        for unit in ['m', 'm/s', 'rad', 'deg']:
            with pytest.raises(UnitsError):
                np.arccosh(QFloat(1.0, unit=unit))

    def test_qfloat_np_arctanh(self):
        qf = QFloat(0.0, 0.01)
        res = np.arctanh(qf)
        assert_almost_equal(res.nominal, 0.0)
        assert_almost_equal(res.std_dev, 0.01)
        assert_equal(res.unit, units.Unit('rad'))

        qf = QFloat([0.1, 0.5, 1.0], [0.01, 0.2, 0.3])
        res = np.arctanh(qf)
        assert_almost_equal(res.nominal, [0.1003353, 0.5493061, np.inf])
        assert_almost_equal(res.std_dev, [0.010101 , 0.2666667, np.inf])
        assert_equal(res.unit, units.Unit('rad'))

        # Invalid units
        for unit in ['m', 'm/s', 'rad', 'deg']:
            with pytest.raises(UnitsError):
                np.arctanh(QFloat(1.0, unit=unit))