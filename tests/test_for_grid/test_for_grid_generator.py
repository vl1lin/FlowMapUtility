from Grid_Generation.grid_generator import GridGenerator
from Grid_Generation.grid_info import GridInfo
import numpy as np
import pytest



def test_for_grid_generator_output_type():
    grid = GridGenerator(
        vsl_range=(0.1, 10.0),
        vsg_range=(10.0, 20.0),
        resolution=100,
        log_scale=True,
    )
    info = grid.grid_generator()
    assert isinstance(info, GridInfo)

def test_for_grid_generator_log_scale():
    grid = GridGenerator(
        vsl_range=(0.1, 0.5),
        vsg_range=(10.0, 15.0),
        resolution=10,
        log_scale=True,
    )
    info = grid.grid_generator()
    assert grid.log_scale is True
    assert np.all(info.vsl_1d == np.logspace(0.1, 0.5, 10))
    assert np.all(info.vsg_1d == np.logspace(10.0, 15.0, 10))
    assert info.vsl_2d.shape == (10, 10)
    assert info.vsg_2d.shape == (10, 10)

def test_for_grid_generator_not_log_scale():
    grid = GridGenerator(
        vsl_range=(0.1, 0.5),
        vsg_range=(10.0, 15.0),
        resolution=10,
        log_scale=False,
    )
    info = grid.grid_generator()
    assert grid.log_scale is False
    assert np.all(info.vsl_1d == np.linspace(0.1, 0.5, 10))
    assert np.all(info.vsg_1d == np.linspace(10.0, 15.0, 10))
    assert info.vsl_2d.shape == (10, 10)
    assert info.vsg_2d.shape == (10, 10)

def test_for_grid_generator_emergency_lin_scale():
    grid = GridGenerator(
        vsl_range=(-0.1, 0.5),
        vsg_range=(-1.0, 5.0),
        resolution=10,
        log_scale=True,
    )
    with pytest.warns(UserWarning):
        info = grid.grid_generator()
    assert grid.log_scale is False
    assert np.all(info.vsl_1d == np.linspace(-0.1, 0.5, 10))
    assert np.all(info.vsg_1d == np.linspace(-1.0, 5.0, 10))
    assert info.vsl_2d.shape == (10, 10)
    assert info.vsg_2d.shape == (10, 10)
