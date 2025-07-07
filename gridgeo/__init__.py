"""GridGeo."""

from gridgeo.gridgeo import GridGeo

__all__ = ["GridGeo"]

try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"
