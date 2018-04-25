from itertools import zip_longest

from gridgeo.cfvariable import _filled_masked, _make_grid

from hypothesis.extra.numpy import array_shapes

import numpy as np

import pytest

from shapely.geometry import MultiPolygon


@pytest.fixture
def make_coords():
    x = y = np.array([1, 2, 3, 4], np.int)
    x, y = np.meshgrid(x, y)
    return np.concatenate([x[..., None], y[..., None, ]], axis=2)


def test__make_grid_raises():
    with pytest.raises(ValueError):
        shape = array_shapes(min_dims=1, max_dims=2)
        _make_grid(np.empty(shape.example()))
    with pytest.raises(ValueError):
        shape = array_shapes(min_dims=4, max_dims=10)
        _make_grid(np.empty(shape.example()))


def test__valid_coords():
    coords = make_coords()
    polygons = _make_grid(coords)
    assert len(polygons) == 9
    assert (polygons[0] == np.array([[1, 1], [2, 1], [2, 2], [1, 2]], np.int)).all()
    assert (polygons[-1] == np.array([[3, 3], [4, 3], [4, 4], [3, 4]], np.int)).all()


def test__valid_geometry():
    coords = make_coords()
    polygons = _make_grid(coords)
    geometry = MultiPolygon(list(zip_longest(polygons, [])))
    assert len(geometry) == 9
    assert geometry[0].centroid.x == 1.5
    assert geometry[0].centroid.y == 1.5
    assert geometry.bounds == (1, 1, 4, 4)


def test__filled_masked():
    marr = np.ma.MaskedArray(
        data=[1, 2, 3, 4],
        mask=[False, False, True, False],
        dtype=np.float,
        fill_value=0,
    )
    arr = _filled_masked(marr)
    assert np.isnan(arr[2])
