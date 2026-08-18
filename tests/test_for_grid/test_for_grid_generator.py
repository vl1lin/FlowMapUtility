import numpy as np
import pytest

from flowmaputility.grid.generator import GridGenerator
from flowmaputility.grid.info import GridInfo


def test_for_grid_generator_output_type() -> None:
    grid = GridGenerator(
        vsl_range=(0.1, 10.0),
        vsg_range=(10.0, 20.0),
        resolution=100,
        log_scale=True,
    )
    info = grid.generate()
    assert isinstance(info, GridInfo)


def test_for_grid_generator_log_scale(create_grid_generator: GridGenerator) -> None:
    info = create_grid_generator.generate()
    assert create_grid_generator.log_scale is True
    assert np.all(info.vsl_1d == np.logspace(np.log10(0.1), np.log10(0.5), 10))
    assert np.all(info.vsg_1d == np.logspace(np.log10(10.0), np.log10(15.0), 10))
    assert info.vsl_2d.shape == (10, 10)
    assert info.vsg_2d.shape == (10, 10)


def test_for_grid_generator_2d(create_small_grid_generator: GridGenerator) -> None:
    x = create_small_grid_generator._generate_2d_array_x(np.arange(3))
    y = create_small_grid_generator._generate_2d_array_y(np.arange(3))
    assert np.all(x == np.array([[0.0, 1.0, 2.0], [0.0, 1.0, 2.0], [0.0, 1.0, 2.0]]))
    assert np.all(y == np.array([[2.0, 2.0, 2.0], [1.0, 1.0, 1.0], [0.0, 0.0, 0.0]]))


def test_for_grid_generator_lin_scale(create_lin_grid_generator: GridGenerator) -> None:
    info = create_lin_grid_generator.generate()
    assert create_lin_grid_generator.log_scale is False
    assert np.all(info.vsl_1d == np.linspace(0.1, 0.5, 10))
    assert np.all(info.vsg_1d == np.linspace(10.0, 15.0, 10))
    assert info.vsl_2d.shape == (10, 10)
    assert info.vsg_2d.shape == (10, 10)


def test_for_grid_generator_emergency_lin_scale(
    create_emergency_grid_generator: GridGenerator,
) -> None:
    info = create_emergency_grid_generator.generate()
    with pytest.warns(UserWarning):
        info = create_emergency_grid_generator.generate()
    assert create_emergency_grid_generator.log_scale is False
    assert np.all(info.vsl_1d == np.linspace(-0.1, 0.5, 10))
    assert np.all(info.vsg_1d == np.linspace(-1.0, 5.0, 10))
    assert info.vsl_2d.shape == (10, 10)
    assert info.vsg_2d.shape == (10, 10)
