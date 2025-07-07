from pathlib import Path

import numpy as np
from shapely.geometry import MultiPolygon, Polygon

import gridgeo

# The netcdf file used here is based on
# $ url="http://colossus.dl.stevens-tech.edu:8080/thredds/dodsC/latest/Complete_gcmplt.nc"
# $ ncks -d time,0 -d sigma,0 -v temp $url unknown_2d.nc
#
# $ url="http://thredds.cencoos.org/thredds/dodsC/CENCOOS_CA_ROMS_FCST.nc"
# $ ncks -d time,0 -d depth,0 -v temp $url unknown_1d.nc
#
# then a .cdl was created and edit to reduce the size on the .nc.

p = Path(__file__).parent.absolute()

fname = p.joinpath("data", "unknown_1d.nc")

grid = gridgeo.GridGeo(fname, standard_name="sea_water_potential_temperature")
npoly = 136500

_iterables = (tuple, list, np.ndarray)


def test_mesh():
    assert grid.mesh == "unknown_1d"


def test__str__():
    assert grid.__str__() == grid.mesh


def test_outline():
    assert isinstance(grid.outline, (MultiPolygon, Polygon))


def test_polygons():
    assert isinstance(grid.polygons, _iterables)
    assert all(isinstance(p, _iterables) for p in grid.polygons)
    n_nodes = 4
    assert all(len(p) == n_nodes for p in grid.polygons)


def test_geometry():
    assert isinstance(grid.geometry, MultiPolygon)


def test_polygons_len():
    assert len(grid.polygons) == npoly
    assert len(grid.geometry.geoms) == npoly


def test_geo_interface():
    assert isinstance(grid.__geo_interface__, dict)


def test_to_geojson():
    geojson = grid.to_geojson(float_precision=2)
    assert geojson["type"] == "Feature"
    assert isinstance(geojson, dict)
    assert geojson["geometry"]["type"] == "MultiPolygon"
    assert geojson["properties"] == {
        "description": "",
        "fill": "555555",
        "fill-opacity": 0.6,
        "marker-color": "7e7e7e",
        "marker-size": "medium",
        "marker-symbol": "",
        "stroke": "555555",
        "stroke-opacity": 1,
        "stroke-width": 2,
        "title": grid.mesh,
    }
    coords = geojson["geometry"]["coordinates"]
    assert len(coords) == npoly
    n_nodes = 5  # squares are 4+1
    assert len(coords[0][0]) == n_nodes
    assert str(coords[0][0][0][0]) == "232.5"
