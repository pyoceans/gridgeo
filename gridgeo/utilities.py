from __future__ import (absolute_import, division, print_function)


import pyugrid
import pysgrid

import numpy as np

from pysgrid.custom_exceptions import SGridNonCompliantError

from netCDF4 import Dataset
from shapely.geometry.polygon import Polygon


__all__ = ['load_grid',
           'rasterize']


def load_grid(nc):
    """
    Takes a `nc` (netCDF4-python object), a file/URL path, or an
    `iris.cube.Cube` instance.

    Returns a tuple with the `grid` object, `mesh` type, and grid `polygons`.

    """

    grid = None
    mesh = 'non-compliant'

    if nc.__class__.__name__ == 'Cube':
        polygons = _parse_cube(nc)
        return grid, polygons, mesh
    elif isinstance(nc, Dataset):
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

    # When all fails try non-compliant `grid` type.
    polygons = _parse_grid(nc)
    return grid, polygons, mesh


def _parse_ugrid(ugrid):
    """
    Return a polygons generator from an `ugrid` object.

    """
    lon = ugrid.nodes[:, 0]
    lat = ugrid.nodes[:, 1]
    triangles = ugrid.faces[:]

    return (Polygon(zip(lon[k], lat[k])) for k in triangles)


def _parse_sgrid(sgrid):
    """
    Return a polygons generator from an `sgrid` object.

    NOTE: Works only for the grid center. The edges are not implemented in
    `pysgrid` yet.

    """
    coords = sgrid.centers.copy()
    return _make_grid(coords)


def _parse_grid(nc):
    """
    Return a polygons generator from a `grid`.

    """

    # TODO: A more more robust way to find the axis would be iris' CF model.
    # https://github.com/SciTools/iris/blob/24a4be25e0936edba6f0ff0432f1e56233969b7a/lib/iris/fileformats/_pyke_rules/fc_rules_cf.krb#L1318-L1401
    lon = nc.get_variables_by_attributes(_CoordinateAxisType='Lon')
    lat = nc.get_variables_by_attributes(_CoordinateAxisType='Lat')
    if len(lon) > 1 or len(lat) > 1:
        msg = 'Found more than 1 grid.\n{!r}, {!r}'.format
        raise ValueError(msg(lon, lat))
    elif not lon or not lat:
        raise ValueError('Could not find the grid coordinates.')
    else:
        lon, lat = lon[0][:], lat[0][:]

    if lon.ndim == 1 and lat.ndim == 1:
        lon, lat = np.meshgrid(lon, lat)
    coords = np.stack([lon, lat], axis=2)
    return _make_grid(coords)


def _parse_cube(cube):
    lon = cube.coord(axis='X').points
    lat = cube.coord(axis='Y').points
    if lon.ndim == 1 and lat.ndim == 1:
        lon, lat = np.meshgrid(lon, lat)
    coords = np.stack([lon, lat], axis=2)
    return _make_grid(coords)


def _make_grid(coords):
    M, N, L = coords.shape
    points = np.concatenate((coords[0:-1, 0:-1],
                             coords[0:-1, 1:],
                             coords[1:, 1:],
                             coords[1:, 0:-1],
                             coords[0:-1, 0:-1]), axis=L)

    points = points.reshape(((M-1) * (N-1), 5, L))
    return (Polygon(p) for p in points)


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
    TODO: re-write this using rasterio.

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
