from unittest.mock import Mock, patch

import numpy as np

from flowmaputility.grid.info import GridInfo
from flowmaputility.visualization.palette import DEFAULT_COLORS, PATTERN_NAMES
from flowmaputility.visualization.visualizer import MapVisualizer


def _make_grid() -> GridInfo:
    vsl_1d = np.array([0.1, 0.2, 0.3])
    vsg_1d = np.array([1.0, 2.0, 3.0])
    vsl_2d = np.ones((3, 3)) * vsl_1d
    vsg_2d = vsg_1d[:, np.newaxis] * np.ones((3, 3))
    return GridInfo(vsl_1d, vsg_1d, vsl_2d, vsg_2d, 3, True)


def test_for_invert_axes_default_false():
    manager = MapVisualizer(Mock(), Mock(), Mock())
    assert manager.invert_axes is False


def test_for_plot_grid_not_inverted_by_default():
    grid = _make_grid()
    manager = MapVisualizer(Mock(), grid, Mock(), invert_axes=False)
    plot_grid = manager._get_plot_grid()
    assert plot_grid is grid
    assert np.array_equal(plot_grid.vsl_1d, grid.vsl_1d)
    assert np.array_equal(plot_grid.vsg_1d, grid.vsg_1d)
    assert np.array_equal(plot_grid.vsl_2d, grid.vsl_2d)
    assert np.array_equal(plot_grid.vsg_2d, grid.vsg_2d)


def test_for_plot_grid_inverted():
    grid = _make_grid()
    manager = MapVisualizer(Mock(), grid, Mock(), invert_axes=True)
    plot_grid = manager._get_plot_grid()
    assert np.array_equal(plot_grid.vsl_1d, grid.vsg_1d)
    assert np.array_equal(plot_grid.vsg_1d, grid.vsl_1d)
    assert np.array_equal(plot_grid.vsl_2d, grid.vsg_2d)
    assert np.array_equal(plot_grid.vsg_2d, grid.vsl_2d)


def test_for_original_grid_not_mutated_after_run():
    grid = _make_grid()
    code_matrix = np.array([[105, 103, 101], [103, 101, 105], [101, 105, 103]])
    manager = MapVisualizer(
        code_matrix, grid, "ansari", show_plot=False, invert_axes=True
    )
    manager.run()
    assert np.array_equal(manager.grid.vsl_1d, grid.vsl_1d)
    assert np.array_equal(manager.grid.vsg_1d, grid.vsg_1d)
    assert np.array_equal(manager.grid.vsl_2d, grid.vsl_2d)
    assert np.array_equal(manager.grid.vsg_2d, grid.vsg_2d)


def test_for_unuique_patterns():
    code_matrix = np.array([[105, 103, 101], [103, 101, 105], [101, 105, 103]])
    manager = MapVisualizer(code_matrix, Mock(), Mock())
    unique_codes = manager._get_unique_patterns()
    assert unique_codes.shape == (3,)
    assert unique_codes[0] == 101
    assert unique_codes[1] == 103
    assert unique_codes[2] == 105


def test_for_pattern_names():
    sorted_unique_codes = np.array([101, 103, 105])
    pattern_names = MapVisualizer._get_pattern_names(sorted_unique_codes)
    assert pattern_names == [PATTERN_NAMES.get(i) for i in sorted_unique_codes]


def test_for_pattern_names_exception():
    sorted_unique_codes = np.array([101, 103, 105, 200, 199, 405])
    pattern_names = MapVisualizer._get_pattern_names(sorted_unique_codes)
    assert "Такой код не предусмотрен" in pattern_names
    assert "Неизвестно" in pattern_names


def test_for_pattern_colors():
    sorted_unique_codes = np.array([101, 103, 105])
    patterns_colors = MapVisualizer._get_colors(sorted_unique_codes)
    assert len(patterns_colors) == 3
    assert patterns_colors == [DEFAULT_COLORS.get(i) for i in sorted_unique_codes]


def test_for_color_bounds():
    sorted_unique_codes = np.array([101, 103, 105])
    color_bounds = MapVisualizer._create_color_bounds(sorted_unique_codes)
    assert len(color_bounds) == 4
    assert color_bounds == [100.5, 102.5, 104.5, 105.5]


@patch("flowmaputility.visualization.visualizer.plt")
def test_for_saveing_map(mock_plt):
    MapVisualizer._save_map("some_path")
    mock_plt.savefig.assert_called_once_with("some_path", dpi=300, bbox_inches="tight")


@patch("flowmaputility.visualization.visualizer.plt")
def test_for_not_saving_map(mock_plt):
    MapVisualizer._save_map(None)
    mock_plt.savefig.assert_not_called()


@patch("flowmaputility.visualization.visualizer.plt")
def test_for_showing_map(mock_plt):
    MapVisualizer._show_map(True)
    mock_plt.show.assert_called_once()
    mock_plt.close.assert_not_called()


@patch("flowmaputility.visualization.visualizer.plt")
def test_for_hiding_map(mock_plt):
    MapVisualizer._show_map(False)
    mock_plt.show.assert_not_called()
    mock_plt.close.assert_called_once()
