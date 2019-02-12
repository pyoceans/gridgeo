from gridgeo.gridgeo import GridGeo

__all__ = ["GridGeo"]

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
