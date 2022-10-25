from pathlib import Path

from setuptools import find_packages, setup

rootpath = Path(__file__).parent.absolute()

def read(*parts):
    return open(rootpath.joinpath(*parts), "r").read()


with open("requirements.txt") as f:
    require = f.readlines()
install_requires = [r.strip() for r in require]

setup(
    name="gridgeo",
    description="Convert UGRID, SGRID, and non-compliant ocean model grids to geo-like objects",  # noqa
    license="BSD-3-Clause",
    long_description=f'{read("README.md")}',
    long_description_content_type="text/markdown",
    author="Filipe Fernandes",
    author_email="ocefpaf@gmail.com",
    url="https://github.com/pyoceans/gridgeo",
    keywords=["geojson", "shapefile", "ocean models", "ugrid", "sgrid"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    platforms="any",
    packages=find_packages(),
    extras_require={"testing": ["pytest"]},
    install_requires=install_requires,
    entry_points={"console_scripts": ["gridio = gridgeo.gridio:main"]},
    use_scm_version={
        "write_to": "gridgeo/_version.py",
        "write_to_template": '__version__ = "{version}"',
        "tag_regex": r"^(?P<prefix>v)?(?P<version>[^\+]+)(?P<suffix>.*)?$",
    },
    setup_requires=['setuptools_scm'],
)