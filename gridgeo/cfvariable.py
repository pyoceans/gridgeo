"""CFVariable."""

import numpy as np

from gridgeo.ugrid import ugrid


def _make_grid(coords):
    ndim = 3
    if coords.ndim != ndim:
        msg = f"Expected 3 dimension array, got {coords.ndim}."
        raise ValueError(msg)
    M, N, L = coords.shape  # noqa: N806
    polygons = np.concatenate(
        (
            coords[0:-1, 0:-1],
            coords[0:-1, 1:],
            coords[1:, 1:],
            coords[1:, 0:-1],
        ),
        axis=L,
    ).reshape(((M - 1) * (N - 1), 4, L))
    return [p for p in polygons if not np.isnan(p).any()]


def _filled_masked(arr):
    if hasattr(arr, "filled"):
        return arr.filled(fill_value=np.nan)
    return arr


class CFVariable:
    """CFVariable."""

    def __init__(self, nc, **kwargs):
        """NB: This should be done when slicing a CFVariable in pocean-core.
        This class is only a temporary workaround until something better.

        """
        self._nc = nc
        variables = self._nc.get_variables_by_attributes(**kwargs)
        if len(variables) > 1:
            msg = f"Found more than 1 variable with criteria {kwargs}"
            raise ValueError(msg)
        if not variables:
            msg = f"Could not find any variables with criteria {kwargs}"
            raise ValueError(msg)
        self._variable = variables[0]
        self._coords = self._variable.coordinates.split()

    def _filter_coords(self, variables):
        valid_coords = [var for var in variables if var.name in self._coords]

        if len(valid_coords) != 1:
            msg = f"Expected a single coord, got '{valid_coords}'."
            raise ValueError(msg)
        return valid_coords[0]

    def axis(self, name):
        return getattr(self, f"{name.lower()}_axis")()

    def t_axis(self):
        tvars = list(
            set(
                self._nc.get_variables_by_attributes(
                    axis=lambda x: x and str(x).lower() == "t",
                )
                + self._nc.get_variables_by_attributes(
                    standard_name=lambda x: str(x) == "time",
                )
                + self._nc.get_variables_by_attributes(
                    _CoordinateAxisType=lambda x: str(x).lower() == "time",
                ),
            ),
        )
        # For _CoordinateAxisType: Time
        return self._filter_coords(tvars)

    def crs(self):
        crs = getattr(self._variable, "grid_mapping", None)
        if crs:
            crs = self._nc[crs]
        return crs

    def x_axis(self):
        xnames = ["longitude", "grid_longitude", "projection_x_coordinate"]
        xunits = [
            "degrees_east",
            "degree_east",
            "degree_E",
            "degrees_E",
            "degreeE",
            "degreesE",
        ]
        xvars = list(
            set(
                self._nc.get_variables_by_attributes(
                    axis=lambda x: x and str(x).lower() == "x",
                )
                + self._nc.get_variables_by_attributes(
                    standard_name=lambda x: x and str(x).lower() in xnames,
                )
                + self._nc.get_variables_by_attributes(
                    units=lambda x: x and str(x).lower() in xunits,
                ),
            ),
        )
        return self._filter_coords(xvars)

    def y_axis(self):
        ynames = ["latitude", "grid_latitude", "projection_y_coordinate"]
        yunits = [
            "degrees_north",
            "degree_north",
            "degree_N",
            "degrees_N",
            "degreeN",
            "degreesN",
        ]
        yvars = list(
            set(
                self._nc.get_variables_by_attributes(
                    axis=lambda x: x and str(x).lower() == "y",
                )
                + self._nc.get_variables_by_attributes(
                    standard_name=lambda x: x and str(x).lower() in ynames,
                )
                + self._nc.get_variables_by_attributes(
                    units=lambda x: x and str(x).lower() in yunits,
                ),
            ),
        )
        return self._filter_coords(yvars)

    def z_axis(self):
        znames = [
            "atmosphere_ln_pressure_coordinate",
            "atmosphere_sigma_coordinate",
            "atmosphere_hybrid_sigma_pressure_coordinate",
            "atmosphere_hybrid_height_coordinate",
            "atmosphere_sleve_coordinate",
            "ocean_sigma_coordinate",
            "ocean_s_coordinate",
            "ocean_s_coordinate_g1",
            "ocean_s_coordinate_g2",
            "ocean_sigma_z_coordinate",
            "ocean_double_sigma_coordinate",
        ]
        zvars = list(
            set(
                self._nc.get_variables_by_attributes(
                    axis=lambda x: x and str(x).lower() == "z",
                )
                + self._nc.get_variables_by_attributes(
                    positive=lambda x: x and str(x).lower() in ("up", "down"),
                )
                + self._nc.get_variables_by_attributes(
                    standard_name=lambda x: x and str(x).lower() in znames,
                ),
            ),
        )
        return self._filter_coords(zvars)

    def topology(self):
        vnames = ["grid_topology", "mesh_topology"]
        topologies = self._nc.get_variables_by_attributes(
            cf_role=lambda v: v in vnames,
        )

        if not topologies:
            if self.x_axis().ndim == 1 == self.y_axis().ndim == 1:
                return "unknown_1d"
            ndim = 2
            if self.x_axis().ndim == ndim == self.y_axis().ndim == ndim:
                return "unknown_2d"
            msg = f"Could not identify the topology for {self._nc}."
            raise ValueError(msg)

        if topologies and len(topologies) > 1:
            msg = f"Expected 1 topology variable, got {len(topologies)}."
            raise ValueError(msg)

        mesh = topologies[0]
        dims = getattr(mesh, "topology_dimension", None)
        cf_role = getattr(mesh, "cf_role", None)

        if cf_role == "mesh_topology" and dims in (1, 2):
            return "ugrid"
        n_topo = 2
        if cf_role == "grid_topology" and dims == n_topo:
            return "sgrid"
        return None

    def polygons(self):
        if self.topology() == "ugrid":
            grid = ugrid(self._nc)
            node_x = grid["nodes"]["x"]
            node_y = grid["nodes"]["y"]
            faces = grid["faces"]
            return [
                (list(zip(node_x[k], node_y[k], strict=False))) for k in faces
            ]

        if self.topology() == "sgrid":
            x, y = self.x_axis()[:], self.y_axis()[:]
            coords = np.concatenate([x[..., None], y[..., None]], axis=2)
            return _make_grid(coords)

        if self.topology() == "unknown_1d":
            x, y = self.x_axis()[:], self.y_axis()[:]
            # Some non-compliant grids, like NYHOPS,
            # may have missing_value/fill_value.
            x = _filled_masked(x)
            y = _filled_masked(y)
            if hasattr(y, "filled"):
                y = y.filled(fill_value=np.nan)
            x, y = np.meshgrid(x, y)
            coords = np.stack([x, y], axis=2)
            return _make_grid(coords)

        if self.topology() == "unknown_2d":
            x, y = self.x_axis()[:], self.y_axis()[:]
            # Some non-compliant grids, like NYHOPS,
            # may have missing_value/fill_value.
            x = _filled_masked(x)
            y = _filled_masked(y)
            coords = np.concatenate([x[..., None], y[..., None]], axis=2)
            return _make_grid(coords)
        return None

    # Replication of the `netCDF4.Variable` object via composition.
    def __getitem__(self, key):
        return self._variable.__getitem__(key)

    def __repr__(self):
        return self._variable.__repr__()

    @property
    def units(self):
        return self._variable.units

    @property
    def standard_name(self):
        return self._variable.standard_name

    @property
    def long_name(self):
        return self._variable.long_name

    @property
    def coordinates(self):
        return self._variable.coordinates

    @property
    def ndim(self):
        return self._variable.ndim

    @property
    def size(self):
        return self._variable.size

    @property
    def shape(self):
        return self._variable.shape

    @property
    def scale(self):
        return self._variable.scale

    @property
    def datatype(self):
        return self._variable.datatype

    @property
    def dimensions(self):
        return self._variable.dimensions

    @property
    def dtype(self):
        return self._variable.dtype

    @property
    def field(self):
        return self._variable.field

    @property
    def name(self):
        return self._variable.name

    @property
    def mask(self):
        return self._variable.mask

    @property
    def _FillValue(self):
        return self._variable._FillValue

    @property
    def _ChunkSizes(self):
        return self._variable._ChunkSizes

    @property
    def chartostring(self):
        return self._variable.chartostring

    def chunking(self):
        return self._variable.chunking()

    def endian(self):
        return self._variable.endian()

    def filters(self):
        return self._variable.filters()

    def group(self):
        return self._variable.group()

    def ncattrs(self):
        return self._variable.ncattrs()
