from __future__ import (absolute_import, division, print_function)

import os
import pytest

import gridgeo

data_path = os.path.join(os.path.dirname(__file__), 'data')

espresso_string = os.path.join(data_path,
                               'ESPRESSO_Real-Time_v2_Averages_Best.nc')

point_time_series_string = os.path.join(data_path,
                                        'point_time_series.nc')


def test_more_than_one_grid():
    with pytest.raises(ValueError):
        gridgeo.GridGeo(espresso_string)


def test_no_grid():
    with pytest.raises(ValueError):
        gridgeo.GridGeo(point_time_series_string)
