from pathlib import Path

import gridgeo

import numpy as np

from shapely.geometry import MultiPolygon, Polygon

p = Path(__file__).parent.absolute()

fname = p.joinpath('data', 'unknown_2d.nc')

grid = gridgeo.GridGeo(
    fname,
    standard_name='sea_water_temperature'
    )
npoly = 12706


_iterables = (tuple, list, np.ndarray)


def test_mesh():
    assert grid.mesh == 'unknown_2d'


def test__str__():
    assert grid.__str__() == grid.mesh


def test_outline():
    assert isinstance(grid.outline, (MultiPolygon, Polygon))


def test_polygons():
    assert isinstance(grid.polygons, _iterables)
    assert all((isinstance(p, _iterables) for p in grid.polygons))
    assert all((len(p) == 4 for p in grid.polygons))


def test_geometry():
    assert isinstance(grid.geometry, MultiPolygon)


def test_polygons_len():
    assert len(grid.polygons) == npoly
    assert len(grid.geometry) == npoly


def test_geo_interface():
    assert isinstance(grid.__geo_interface__, dict)


def test_to_geojson():
    geojson = grid.to_geojson(float_precision=2)
    assert geojson['type'] == 'Feature'
    assert isinstance(geojson, dict)
    assert geojson['geometry']['type'] == 'MultiPolygon'
    assert geojson['properties'] == {
        'description': '',
        'fill': '555555',
        'fill-opacity': 0.6,
        'marker-color': '7e7e7e',
        'marker-size': 'medium',
        'marker-symbol': '',
        'stroke': '555555',
        'stroke-opacity': 1,
        'stroke-width': 2,
        'title': grid.mesh
        }
    coords = geojson['geometry']['coordinates']
    assert len(coords) == npoly
    assert len(coords[0][0]) == 5  # squares are 4+1
    assert str(coords[0][0][0][0]) == '-74.29'
