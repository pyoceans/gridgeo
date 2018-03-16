from __future__ import (absolute_import, division, print_function)

import gridgeo

from shapely.geometry import MultiPolygon, Polygon


url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_BOSTON_FORECAST.nc'  # noqa


grid = gridgeo.GridGeo(
    url,
    standard_name='sea_water_potential_temperature'
     )
npoly = 145141


def test_mesh():
    assert grid.mesh == 'ugrid'


def test__str__():
    assert grid.__str__() == grid.mesh


def test_outline():
    assert isinstance(grid.outline, (MultiPolygon, Polygon))


def test_polygons():
    assert isinstance(grid.polygons, MultiPolygon)


def test_polygons_len():
    assert len(grid.polygons) == npoly


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
    assert len(coords[0][0]) == 4  # triangles are 3+1
    assert str(coords[0][0][0][0]) == '-70.83'
