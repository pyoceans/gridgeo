from __future__ import (absolute_import, division, print_function)


import pyugrid
import pysgrid

import numpy as np

from pysgrid.custom_exceptions import SGridNonCompliantError

from netCDF4 import Dataset
from shapely.geometry import MultiPolygon
from shapely.geometry.polygon import Polygon


__all__ = ['load_grid',
           'rasterize']


def load_grid(nc):
    """
    Takes a `nc` netCDF4-python object or a file/URL path.
    Returns a tuplw=e with the grid object and the polygons to draw it.

    """

    if isinstance(nc, Dataset):
        pass
    else:
        nc = Dataset(nc)

    try:
        grid = pysgrid.from_nc_dataset(nc)
        polygons = _parse_sgrid(grid)
        mesh = 'sgrid'
        return grid, polygons, mesh
    except (SGridNonCompliantError, KeyError):
        pass
    try:
        grid = pyugrid.UGrid.from_nc_dataset(nc)
        polygons = _parse_ugrid(grid)
        mesh = 'ugrid'
        return grid, polygons, mesh
    except ValueError:
        pass

    # When all fails try a `rgrid` type.
    grid = None
    polygons = _parse_rgrid(nc)
    mesh = 'rgrid'
    return grid, polygons, mesh


def _parse_ugrid(ugrid):
    """
    The `ugrid` object is parsed as a shapely `MultiPolygon` containing
    several `Polygon`s, for example, the triangles of a triangular mesh.

    """
    lon = ugrid.nodes[:, 0]
    lat = ugrid.nodes[:, 1]
    triangles = ugrid.faces[:]

    return MultiPolygon([Polygon(zip(lon[k], lat[k])) for k in triangles])


def _parse_sgrid(sgrid):
    """
    The `sgrid` object is parsed as a collection of `Polygon`s.

    NOTE: Works only for the grid center because `sgrid` does not provide an
    agnostic way to access the edges yet.

    """
    coords = sgrid.centers.copy()
    return _make_rgrid(coords)


def _parse_rgrid(nc):
    """
    Parse a regular grid as a collection of `Polygon`s.

    FIXME: `long_name` only is very flaky!

    """

    lon_names = lambda v: v in ['longitude', 'Longitude',
                                'lon', 'Lon', 'long', 'Long']
    lat_names = lambda v: v in ['latitude', 'Latitude', 'lat', 'Lat']
    lon = nc.get_variables_by_attributes(long_name=lon_names)[0][:]
    lat = nc.get_variables_by_attributes(long_name=lat_names)[0][:]

    coords = np.meshgrid(lon, lat)
    coords = np.stack([coords[0], coords[1]], axis=2)
    return _make_rgrid(coords)


def _make_rgrid(coords):
    M, N, L = coords.shape
    points = np.concatenate((coords[0:-1, 0:-1],
                             coords[0:-1, 1:],
                             coords[1:, 1:],
                             coords[1:, 0:-1],
                             coords[0:-1, 0:-1]), axis=L)

    points = points.reshape(((M-1) * (N-1), 5, L))

    return MultiPolygon([Polygon(p) for p in points])


def _trim(fname):
    from PIL import Image, ImageChops
    img = Image.open(fname)
    img = img.convert('RGBA')
    datas = img.getdata()

    new_data = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)

    border = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, border)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        img = img.crop(bbox)
    return np.array(img)


def rasterize(polygons):
    """
    A very amateurish way to make a raster image of the grid ;-)

    """
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    from StringIO import StringIO

    projection = ccrs.PlateCarree()
    fig, ax = plt.subplots(subplot_kw=dict(projection=projection))
    bounds = polygons.bounds

    ax.set_extent([bounds[0], bounds[2], bounds[1], bounds[3]])
    kw = dict(linestyle='-', color='darkgray', linewidth=0.5)
    ax.add_geometries(polygons, ccrs.PlateCarree(),
                      facecolor='none', **kw)
    ax.axis('off')

    imgdata = StringIO()
    fig.savefig(imgdata, transparent=True, dpi=150)
    imgdata.seek(0)
    img = _trim(imgdata)
    return img
