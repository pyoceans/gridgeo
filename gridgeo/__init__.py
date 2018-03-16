from __future__ import absolute_import, division, print_function

from gridgeo.gridgeo import GridGeo

__version__ = '1.0.0'

__all__ = [
    'GridGeo',
]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
