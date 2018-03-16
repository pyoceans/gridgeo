from __future__ import absolute_import, division, print_function

from itertools import zip_longest

from gridgeo.ugrid import ugrid

import numpy as np

from shapely.geometry import MultiPolygon


def _make_grid(coords):
    M, N, L = coords.shape
    polygons = np.concatenate(
        (
            coords[0:-1, 0:-1],
            coords[0:-1, 1:],
            coords[1:, 1:],
            coords[1:, 0:-1],
        ),
        axis=L
    )

    polygons = polygons.reshape(((M-1) * (N-1), 4, L))
    polygons = [p for p in polygons if not np.isnan(p).any()]
    return MultiPolygon(list(zip_longest(polygons, [])))


def _filled_masked(arr):
    if hasattr(arr, 'filled'):
        return arr.filled(fill_value=np.NaN)
    else:
        return arr


class CFVariable(object):
    def __init__(self, nc, **kwargs):
        """
        FIXME: this should be done when slicing a CFVariable in pocean-core.
        This class is only temporary until something better is created:
        like iris with better slicing, xarray variables that are CF aware,
        or a CFVariable on pocean-core.

        """
        self.nc = nc
        variables = self.nc.get_variables_by_attributes(**kwargs)
        if len(variables) > 1:
            raise ValueError(f'Found more than 1 variable with criteria {kwargs}')
        elif not variables:
            raise ValueError(f'Could not find any variables with criteria {kwargs}')
        else:
            self.Variable = variables[0]
        self.coordinates = self.Variable.coordinates.split()

    def __repr__(self):
        return self.Variable.__repr__()

    def _filter_coords(self, variables):
        for var in variables:
            if var.name in self.coordinates:
                return var
        raise ValueError(f'Could not find a match between {self.coordinates} and {variables}')

    def axis(self, name):
        return getattr(self, '{}_axis'.format(name.lower()))()

    def t_axis(self):
        tvars = list(set(
            self.nc.get_variables_by_attributes(
                axis=lambda x: x and x.lower() == 't'
            ) +
            self.nc.get_variables_by_attributes(
                standard_name=lambda x: x in ['time', 'forecast_reference_time']
            )
        ))
        return self._filter_coords(tvars)

    def x_axis(self):
        """
        CF X axis will have one of the following:
          * The `axis` property has the value ``'X'``
          * Units of longitude (see `cf.Units.islongitude` for details)
          * The `standard_name` property is one of ``'longitude'``,
            ``'projection_x_coordinate'`` or ``'grid_longitude'``
        """
        xnames = ['longitude', 'grid_longitude', 'projection_x_coordinate']
        xunits = [
            'degrees_east',
            'degree_east',
            'degree_E',
            'degrees_E',
            'degreeE',
            'degreesE'
        ]
        xvars = list(set(
            self.nc.get_variables_by_attributes(
                axis=lambda x: x and x.lower() == 'x'
            ) +
            self.nc.get_variables_by_attributes(
                standard_name=lambda x: x and x.lower() in xnames
            ) +
            self.nc.get_variables_by_attributes(
                units=lambda x: x and x.lower() in xunits
            )
        ))
        return self._filter_coords(xvars)

    def y_axis(self):
        ynames = ['latitude', 'grid_latitude', 'projection_y_coordinate']
        yunits = [
            'degrees_north',
            'degree_north',
            'degree_N',
            'degrees_N',
            'degreeN',
            'degreesN'
        ]
        yvars = list(set(
            self.nc.get_variables_by_attributes(
                axis=lambda x: x and x.lower() == 'y'
            ) +
            self.nc.get_variables_by_attributes(
                standard_name=lambda x: x and x.lower() in ynames
            ) +
            self.nc.get_variables_by_attributes(
                units=lambda x: x and x.lower() in yunits
            )
        ))
        return self._filter_coords(yvars)

    def z_axis(self):
        znames = [
            'atmosphere_ln_pressure_coordinate',
            'atmosphere_sigma_coordinate',
            'atmosphere_hybrid_sigma_pressure_coordinate',
            'atmosphere_hybrid_height_coordinate',
            'atmosphere_sleve_coordinate',
            'ocean_sigma_coordinate',
            'ocean_s_coordinate',
            'ocean_s_coordinate_g1',
            'ocean_s_coordinate_g2',
            'ocean_sigma_z_coordinate',
            'ocean_double_sigma_coordinate'
        ]
        zvars = list(set(
            self.nc.get_variables_by_attributes(
                axis=lambda x: x and x.lower() == 'z'
            ) +
            self.nc.get_variables_by_attributes(
                positive=lambda x: x and x.lower() in ['up', 'down']
            ) +
            self.nc.get_variables_by_attributes(
                standard_name=lambda x: x and x.lower() in znames
            )
        ))
        return self._filter_coords(zvars)

    def topology(self):
        vnames = ['grid_topology', 'mesh_topology']
        topologies = self.nc.get_variables_by_attributes(cf_role=lambda v: v in vnames)

        if not topologies:
            if self.x_axis().ndim == 1 and self.y_axis().ndim == 1:
                return 'unknown_1d'
            elif self.x_axis().ndim == 2 and self.y_axis().ndim == 2:
                return 'unknown_2d'
            else:
                raise ValueError(f'Could not identify the topology for {self.nc}.')

        if topologies and len(topologies) > 1:
            raise ValueError(f'Expected 1 topology variable, got {len(topologies)}.')

        mesh = topologies[0]
        dims = getattr(mesh, 'topology_dimension', None)
        cf_role = getattr(mesh, 'cf_role', None)

        if cf_role == 'mesh_topology' and dims in (1, 2):
            return 'ugrid'
        if cf_role == 'grid_topology' and dims == 2:
            return 'sgrid'

    def polygons(self):
        if self.topology() == 'ugrid':
            grid = ugrid(self.nc)
            node_x = grid['nodes']['x']
            node_y = grid['nodes']['y']
            faces = grid['faces']
            polygons = [(list(zip(node_x[k], node_y[k]))) for k in faces]
            return MultiPolygon(list(zip_longest(polygons, [])))

        if self.topology() == 'sgrid':
            x, y = self.x_axis()[:], self.y_axis()[:]
            coords = np.concatenate([x[..., None], y[:][..., None, ]], axis=2)
            return _make_grid(coords)

        if self.topology() == 'unknown_1d':
            x, y = self.x_axis()[:], self.y_axis()[:]
            # Some non-compliant grids, like NYHOPS, may have missing_value/fill_value.
            x = _filled_masked(x)
            y = _filled_masked(y)
            if hasattr(y, 'filled'):
                y = y.filled(fill_value=np.NaN)
            x, y = np.meshgrid(x, y)
            coords = np.stack([x, y], axis=2)
            return _make_grid(coords)

        if self.topology() == 'unknown_2d':
            x, y = self.x_axis()[:], self.y_axis()[:]
            # Some non-compliant grids, like NYHOPS, may have missing_value/fill_value.
            x = _filled_masked(x)
            y = _filled_masked(y)
            coords = np.concatenate([x[..., None], y[:][..., None, ]], axis=2)
            return _make_grid(coords)
