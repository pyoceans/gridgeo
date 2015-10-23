from __future__ import (absolute_import, division, print_function)

import os

import pytest

import pyugrid
import pysgrid

from netCDF4 import Dataset

from grid2json import load_grid

data_path = os.path.join(os.path.dirname(__file__), 'data')


coawst_string = os.path.join(data_path, '00_dir_NYB05.nc')
fvcom_string = os.path.join(data_path, 'FVCOM-Nowcast-Agg.nc')
bad_string = os.path.join(data_path, 'grid.nc')


@pytest.fixture
def coawst_grid():
    return Dataset(coawst_string)


@pytest.fixture
def fvcom_grid():
    return Dataset(fvcom_string)


@pytest.fixture
def bad_grid():
    return Dataset(bad_string)


def test_load_coawst_from_nc():
    nc = coawst_grid()
    assert isinstance(load_grid(nc), pysgrid.sgrid.SGridND)


def test_load_coawst_from_string():
    assert isinstance(load_grid(coawst_string), pysgrid.sgrid.SGridND)


def test_load_fvcom_from_nc():
    nc = fvcom_grid()
    assert isinstance(load_grid(nc), pyugrid.ugrid.UGrid)


def test_load_fvcom_from_string():
    assert isinstance(load_grid(fvcom_string), pyugrid.ugrid.UGrid)


def test_load_bad_from_nc():
    nc = bad_grid()
    assert isinstance(load_grid(nc), None)


def test_load_bad_from_string():
    assert isinstance(load_grid(bad_string), None)
