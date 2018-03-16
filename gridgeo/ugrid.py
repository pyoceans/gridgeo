"""
Lightweight ugrid parser

"""


def _valid_x(var):
    names = ['longitude', 'grid_longitude', 'projection_x_coordinate']
    units = [
        'degrees_east',
        'degree_east',
        'degree_E',
        'degrees_E',
        'degreeE',
        'degreesE'
    ]
    if getattr(var, 'standard_name', None) in names:
        return True
    if getattr(var, 'axis', 'None').lower() == 'x':
        return True
    # Units are mandatory, fail if not present.
    if var.units in units:
        return True
    return False


def _valid_y(var):
    names = ['latitude', 'grid_latitude', 'projection_y_coordinate']
    units = [
        'degrees_north',
        'degree_north',
        'degree_N',
        'degrees_N',
        'degreeN',
        'degreesN'
    ]

    if getattr(var, 'standard_name', None) in names:
        return True
    if getattr(var, 'axis', 'None').lower() == 'y':
        return True
    # Units are mandatory, fail if not present.
    if var.units in units:
        return True
    return False


def _mandatory_attr(var, attribute):
    if not hasattr(var, attribute):
        raise ValueError(f'Could not find required attribute {attribute} in {var}.')
    return


def connectivity_array(connectivity, num_ind):

    array = connectivity[:]
    if array.shape[0] == num_ind:
        array = array.T

    start_index = int(getattr(connectivity, 'start_index', 0))
    if start_index >= 1:
        array -= start_index

    # FIXME: This won't work for more than one flag value.
    flag_values = getattr(connectivity, 'flag_values', None)
    if flag_values:
        array[array == flag_values - start_index] = flag_values
    return array


def get_mesh_var(nc):
    mesh_var = nc.get_variables_by_attributes(cf_role='mesh_topology')
    if not mesh_var:
        raise ValueError(f'Could not find mesh_topology in {nc}')
    if len(mesh_var) > 1:
        raise ValueError(f'Expected 1 mesh_topology variable, found {len(mesh_var)}.')

    mesh_var = mesh_var[0]
    _mandatory_attr(mesh_var, attribute='node_coordinates')
    _mandatory_attr(mesh_var, attribute='topology_dimension')

    if mesh_var.topology_dimension not in (1, 2):
        raise ValueError(f'Expected mesh dimension to be 1 or 2, got {mesh_var.topology_dimension}.')
    return mesh_var


def ugrid(nc):
    mesh_var = get_mesh_var(nc)
    valid_coords = ['node_coordinates', 'face_coordinates', 'edge_coordinates', 'boundary_coordinates']
    valid_connectivity = {
        'face_node_connectivity': 3,
        'face_face_connectivity': 3,
        'boundary_node_connectivity': 2,
        'edge_node_connectivity': 2,
    }

    # Used for compatibility with pyugrid.
    rename = {
        'node_coordinates': 'nodes',
        'face_node_connectivity': 'faces',
        'boundary_node_connectivity': 'boundaries',
        'edge_node_connectivity': 'edges',
    }

    grid = {}
    for key, value in mesh_var.__dict__.items():
        if key in valid_coords:
            coord_names = mesh_var.getncattr(key).strip().split()
            for name in coord_names:
                if _valid_x(nc[name]):
                    x = nc[name][:]
                elif _valid_y(nc[name]):
                    y = nc[name][:]
                else:
                    raise ValueError(f'Could not recoginize axis for {nc[name]}')
            grid.update({key: {'x': x, 'y': y}})
        if key in valid_connectivity.keys():
            connectivity = nc[mesh_var.getncattr(key).strip()]
            num_ind = valid_connectivity[key]
            array = connectivity_array(connectivity, num_ind)
            grid.update({key: array})

    return {rename.get(k, k): v for k, v in grid.items()}
