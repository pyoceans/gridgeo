from __future__ import (absolute_import, division, print_function)

import os
import types

import numpy as np

import iris
from shapely.geometry import MultiPolygon, Polygon

import gridgeo

data_path = os.path.join(os.path.dirname(__file__), 'data')

espresso_string = os.path.join(data_path,
                               'ESPRESSO_Real-Time_v2_Averages_Best.nc')

cube = iris.load_cube(espresso_string, 'sea_water_potential_temperature')

grid = gridgeo.GridGeo(cube)


def test_from_cube():
    assert isinstance(grid.nc, iris.cube.Cube)


def test_grid():
    assert not grid.grid


def test_mesh():
    assert grid.mesh == 'non-compliant'


def test_raster():
    assert isinstance(grid.raster, np.ndarray)


def test_raster_ndim():
    assert grid.raster.ndim == 3


def test_outline():
    assert isinstance(grid.outline, Polygon)


def test_polygons():
    assert isinstance(grid.polygons, MultiPolygon)


def test_geo_interface():
    assert isinstance(grid.__geo_interface__, dict)


def test_polygons_generator():
    assert isinstance(grid._polygons_generator, types.GeneratorType)


def test_to_geojson():
    assert isinstance(grid.to_geojson(), dict)


def test_to_geojson_property():
    geojson = grid.to_geojson()

    properties = ['title', 'description', 'marker-size', 'marker-symbol',
                  'marker-color', 'stroke', 'stroke-opacity', 'stroke-width',
                  'fill', 'fill-opacity']
    for prop in properties:
        assert prop in geojson['properties'].keys()
