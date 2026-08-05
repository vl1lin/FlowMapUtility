import numpy as np
from visualization.map import MapVisualizer
from unittest.mock import Mock, patch
from visualization.map_info import PATTERN_NAMES, DEFAULT_COLORS

def test_for_unuique_patterns():
    code_matrix = np.array([
        [105, 103, 101],
        [103, 101, 105],
        [101, 105, 103]
    ])
    manager = MapVisualizer(code_matrix, Mock())
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

@patch('visualization.map.plt')
def test_for_saveing_map(mock_plt):
    MapVisualizer._save_map("some_path")
    mock_plt.savefig.assert_called_once_with("some_path", dpi=300, bbox_inches='tight')

@patch('visualization.map.plt')
def test_for_not_saving_map(mock_plt):
    MapVisualizer._save_map(None)
    mock_plt.savefig.assert_not_called()

@patch('visualization.map.plt')
def test_for_showing_map(mock_plt):
    MapVisualizer._show_map(True)
    mock_plt.show.assert_called_once()
    mock_plt.close.assert_not_called()

@patch('visualization.map.plt')
def test_for_hiding_map(mock_plt):
    MapVisualizer._show_map(False)
    mock_plt.show.assert_not_called()
    mock_plt.close.assert_called_once()
