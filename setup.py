from setuptools import setup

setup(
    name="gridgeo",
    use_scm_version={
        "write_to": "gridgeo/_version.py",
        "write_to_template": '__version__ = "{version}"',
        "tag_regex": r"^(?P<prefix>v)?(?P<version>[^\+]+)(?P<suffix>.*)?$",
    },
    setup_requires=['setuptools_scm'],
)
