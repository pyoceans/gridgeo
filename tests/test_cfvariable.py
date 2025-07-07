from itertools import zip_longest

import numpy as np
import pytest
from hypothesis import given
from hypothesis.extra.numpy import array_shapes
from shapely.geometry import MultiPolygon

from gridgeo.cfvariable import _filled_masked, _make_grid


@pytest.fixture
def coords():
    x = y = np.array([1, 2, 3, 4], int)
    x, y = np.meshgrid(x, y)
    return np.concatenate([x[..., None], y[..., None]], axis=2)


@given(array_shapes(min_dims=1, max_dims=2))
def test__make_grid_raises_1_2(shape):
    with pytest.raises(ValueError):
        _make_grid(np.empty(shape))


@given(array_shapes(min_dims=4, max_dims=10))
def test__make_grid_raises_4_10(shape):
    with pytest.raises(ValueError):
        _make_grid(np.empty(shape))


def test__valid_coords(coords):
    polygons = _make_grid(coords)
    n_polygons = 9
    assert len(polygons) == n_polygons
    assert (
        polygons[0] == np.array([[1, 1], [2, 1], [2, 2], [1, 2]], int)
    ).all()
    assert (
        polygons[-1] == np.array([[3, 3], [4, 3], [4, 4], [3, 4]], int)
    ).all()


def test__valid_geometry(coords):
    polygons = _make_grid(coords)
    geometry = MultiPolygon(list(zip_longest(polygons, [])))
    n_geoms, center = 9, 1.5
    assert len(geometry.geoms) == n_geoms
    assert geometry.geoms[0].centroid.x == center
    assert geometry.geoms[0].centroid.y == center
    assert geometry.bounds == (1, 1, 4, 4)


def test__filled_masked():
    marr = np.ma.MaskedArray(
        data=[1, 2, 3, 4],
        mask=[False, False, True, False],
        dtype=float,
        fill_value=0,
    )
    arr = _filled_masked(marr)
    assert np.isnan(arr[2])
