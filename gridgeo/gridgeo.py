from __future__ import (absolute_import, division, print_function)

from shapely.ops import cascaded_union

from .utilities import load_grid, rasterize

__all__ = ['GridGeo']


class GridGeo(object):
    """
    GridGeo class takes a nc-like object (netCDF4-python or a netCDF
    file/URL) and parse the grid information.

    """
    def __init__(self, nc, mesh_name=None):
        """
        Return a GridGeo class.
        `nc` : netCDF4-python object or a netCDF file/URL string
        `mesh_name` (string) : can me used to override the the netCDF
                               mesh_name attribute.

        """

        grid, polygons, mesh = load_grid(nc)

        self.nc = nc
        self.grid = grid
        self.polygons = polygons
        self.mesh = mesh
        self._outline = None
        self._raster = None
        self._geo_interface = None

    def __str__(self):
        return 'GeoGrid of {!r}'.format(self.nc)

    def __repr__(self):
        msg = '<Grid type and size: {}, {}>'.format
        return msg(self.mesh, len(self.polygons))

    def _repr_svg_(self):
        return self.outline

    @property
    def outline(self):
        if self._outline is None:
            self._outline = cascaded_union(self.polygons)
        return self._outline

    @property
    def raster(self):
        if self._raster is None:
            self._raster = rasterize(self.polygons)
        return self._raster

    @property
    def __geo_interface__(self):
        if self._geo_interface is None:
            self._geo_interface = self.polygons.__geo_interface__
        return self._geo_interface

    def to_geojson(self, **kw):
        """
        Return a GeoJSON representation of an s-/u-`grid` object.
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
                   'geometry': self.polygons.__geo_interface__}
        return geojson
