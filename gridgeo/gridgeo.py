from __future__ import absolute_import, division, print_function

from copy import copy

from gridgeo.cfvariable import CFVariable
from gridgeo.ugrid import ugrid

import netCDF4

from shapely.ops import cascaded_union

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

        if self.mesh == 'ugrid' and tri:
            grid = ugrid(nc)
            node_x = grid['nodes']['x']
            node_y = grid['nodes']['y']
            faces = grid['faces']
            self.triang = tri.Triangulation(node_x, node_y, triangles=faces)

        self._outline = None
        self._geo_interface = None

    def __str__(self):
        return '{}'.format(self.mesh)

    def __repr__(self):
        return '{!r}'.format(self.outline)

    @property
    def outline(self):
        if self._outline is None:
            self._outline = cascaded_union(self.polygons)
        return self._outline

    @property
    def __geo_interface__(self):
        if self._geo_interface is None:
            self._geo_interface = self.polygons.__geo_interface__
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
        geometry = copy(self.polygons.__geo_interface__)
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
