from __future__ import absolute_import, division, print_function

import os
from copy import copy
from itertools import zip_longest

from gridgeo.cfvariable import CFVariable
from gridgeo.ugrid import ugrid

import netCDF4

from shapely.geometry import MultiPolygon
from shapely.ops import unary_union

try:
    from matplotlib import tri
except ImportError:
    tri = False


def set_precision(coords, precision):
    result = []
    try:
        return round(coords, int(precision))
    except TypeError:
        for coord in coords:
            result.append(set_precision(coord, precision))
    return result


class GridGeo(object):
    """
    GridGeo class takes a nc-like object (netCDF4-python or a netCDF
    file/URL) and parse the grid information.

    """
    def __init__(self, nc, **kwargs):
        """
        Return a GridGeo class.
        nc: netCDF4-python object or a netCDF file/URL string

        """

        if isinstance(nc, netCDF4.Dataset):
            pass
        else:
            nc = netCDF4.Dataset(nc)

        var = CFVariable(nc, **kwargs)

        self.x = var.x_axis()[:]
        self.y = var.y_axis()[:]
        self.mesh = var.topology()
        self.polygons = var.polygons()
        self._geo_interface = None
        self._outline = None
        self._geometry = None

        if self.mesh == 'ugrid' and tri:
            grid = ugrid(nc)
            node_x = grid['nodes']['x']
            node_y = grid['nodes']['y']
            faces = grid['faces']
            self.triang = tri.Triangulation(node_x, node_y, triangles=faces)

    @property
    def geometry(self):
        if self._geometry is None:
            self._geometry = MultiPolygon(list(zip_longest(self.polygons, [])))
        return self._geometry

    def __str__(self):
        return f'{self.mesh}'

    def __repr__(self):
        return f'<GridGeo: {self.mesh}>'

    @property
    def outline(self):
        if self._outline is None:
            self._outline = unary_union(self.geometry)
        return self._outline

    @property
    def __geo_interface__(self):
        if self._geo_interface is None:
            self._geo_interface = self.geometry.__geo_interface__
        return self._geo_interface

    def to_geojson(self, **kw):
        """
        Return a GeoJSON representation of an grid object.
        The `kw` are based on the simplestyle-spec:
        https://github.com/mapbox/simplestyle-spec/tree/master/1.1.0

        """
        title = kw.pop('title', self.mesh)
        description = kw.pop('description', '')
        marker_size = kw.pop('marker-size', 'medium')
        marker_symbol = kw.pop('marker-symbol', '')
        marker_color = kw.pop('marker-color', '7e7e7e')
        stroke = kw.pop('stroke', '555555')
        stroke_opacity = kw.pop('stroke-opacity', 1)
        stroke_width = kw.pop('stroke-width', 2)
        fill = kw.pop('fill', '555555')
        fill_opacity = kw.pop('fill-opacity', 0.6)
        float_precision = kw.pop('float_precision', 6)
        geometry = copy(self.geometry.__geo_interface__)
        geometry['coordinates'] = set_precision(geometry['coordinates'], float_precision)

        geojson = {'type': 'Feature',
                   'properties': {
                       'title': title,
                       'description': description,
                       'marker-size': marker_size,
                       'marker-symbol': marker_symbol,
                       'marker-color': marker_color,
                       'stroke': stroke,
                       'stroke-opacity': stroke_opacity,
                       'stroke-width': stroke_width,
                       'fill': fill,
                       'fill-opacity': fill_opacity,
                       },
                   'geometry': geometry}
        return geojson

    def save(self, filename, fmt=None, **kw):
        formats = ['shp', 'geojson']
        extension = os.path.splitext(filename)[1]

        if not fmt:
            fmt = extension.lstrip('.')

        if fmt not in formats:
            raise ValueError(f'Expected shp or geojson, got {fmt}')

        if extension.lstrip('.') != fmt:
            filename = '.'.join([filename, fmt])

        if fmt == 'geojson':
            import json
            geojson = self.to_geojson(**kw)
            kw = {
                'sort_keys': True,
                'indent': 4,
                'separators': (',', ': ')
            }
            with open(filename, 'w') as f:
                json.dump(geojson, f, **kw)

        if fmt == 'shp':
            import fiona
            name = kw.pop('name', self.mesh)

            schema = {
                'geometry': 'MultiPolygon',
                'properties': {'name': f'str:{len(name)}'}
            }

            with fiona.open(filename, 'w', 'ESRI Shapefile', schema) as f:
                f.write({
                    'geometry': self.__geo_interface__,
                    'properties': {'name': name},
                })
