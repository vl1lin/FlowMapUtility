import pytest
from Grid_Generation.grid_generator import GridGenerator


def test_generator_not_valid_ranges():

    grid = GridGenerator(("", ""), ("", ""), 100, True)  # type: ignore
    with pytest.raises((TypeError, ValueError)):
        grid.validation_befor_grid_generation()

def test_generator_not_valid_len_of_tuple():
    grid = GridGenerator((10, 20, 10), (10), 100, True)  # type: ignore
    with pytest.raises((TypeError, ValueError)):
        grid.validation_befor_grid_generation()

def test_generator_valid_range_not_logical():
    grid = GridGenerator((10, 5), (20, 10), 100, True)  # type: ignore
    with pytest.warns(UserWarning):
        grid.validation_befor_grid_generation()

    assert grid.vsl_range == (5, 10)
    assert grid.vsg_range == (10, 20)

def test_generator_invalid_resolution():
    grid = GridGenerator((5, 10), (10, 20), "invalid", True)  # type: ignore
    with pytest.raises((TypeError, ValueError)):
        grid.validation_befor_grid_generation()

def test_generator_invalid_log_scale():
    grid = GridGenerator((5, 10), (10, 20), 100, "invalid")  # type: ignore
    with pytest.raises(TypeError):
        grid.validation_befor_grid_generation()

def test_generator_all_valid():
    grid = GridGenerator((5, 10), (10, 20), 100, True)  # type: ignore
    grid.validation_befor_grid_generation()
    assert grid.vsl_range == (5, 10)
    assert grid.vsg_range == (10, 20)
    assert grid.resolution == 100
    assert grid.log_scale is True
