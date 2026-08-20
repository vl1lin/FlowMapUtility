from unittest.mock import MagicMock

import numpy as np
from matplotlib.colors import to_rgba
from matplotlib.patches import Patch

from flowmaputility.visualization.palette import DEFAULT_COLORS, PATTERN_NAMES


def test_for_graph_tuner_fig_settings(mock_plt, mock_graph_tuner):
    mock_fig = MagicMock()
    mock_ax = MagicMock()
    mock_plt.subplots.return_value = mock_fig, mock_ax

    tuner = mock_graph_tuner
    tuner._fig_settings()
    assert tuner.fig is mock_fig
    assert tuner.ax is mock_ax

    mock_plt.subplots.assert_called_once_with(figsize=(10, 8))
    mock_fig.patch.set_facecolor.assert_called_once_with("white")


def test_for_graph_tuner_set_scale(mock_graph_tuner):
    tuner = mock_graph_tuner
    assert tuner.set_scale(True) == "log"
    assert tuner.set_scale(False) == "linear"


def test_for_graph_tuner_create_legend(mock_graph_tuner):
    unique_sorted_codes = np.array([101, 103, 105])
    tuner = mock_graph_tuner
    legend_elements = tuner._create_legend(unique_sorted_codes)
    assert len(legend_elements) == 3
    assert all(isinstance(elem, Patch) for elem in legend_elements)

    assert legend_elements[0].get_facecolor() == to_rgba(DEFAULT_COLORS[101])
    assert legend_elements[1].get_facecolor() == to_rgba(DEFAULT_COLORS[103])
    assert legend_elements[2].get_facecolor() == to_rgba(DEFAULT_COLORS[105])

    assert legend_elements[0].get_label() == PATTERN_NAMES[101]
    assert legend_elements[1].get_label() == PATTERN_NAMES[103]
    assert legend_elements[2].get_label() == PATTERN_NAMES[105]


def test_for_graph_tuner_create_legend_unknown_code(mock_graph_tuner):
    unique_sorted_codes = np.array([999])
    tuner = mock_graph_tuner
    legend_elements = tuner._create_legend(unique_sorted_codes)

    assert len(legend_elements) == 1
    assert legend_elements[0].get_label() == "Код 999"
    assert legend_elements[0].get_facecolor() == to_rgba("#FFFFFF")


def test_for_graph_tuner_calling(mock_plt, mock_graph_tuner):
    mock_fig = MagicMock()
    mock_ax = MagicMock()
    mock_plt.subplots.return_value = (mock_fig, mock_ax)

    tuner = mock_graph_tuner
    fig, ax = tuner("ansari", np.array([101, 103]), True)

    assert fig == mock_fig
    assert ax == mock_ax

    mock_plt.subplots.assert_called_once_with(figsize=(10, 8))
    mock_fig.patch.set_facecolor.assert_called_once_with("white")
    mock_ax.set_xscale.assert_called_with("log")
    mock_ax.set_yscale.assert_called_with("log")
    mock_ax.grid.assert_called_once()
    mock_ax.set_xlabel.assert_called_once()
    mock_ax.set_ylabel.assert_called_once()
    mock_ax.set_title.assert_called_once()
    mock_ax.legend.assert_called_once()


def test_for_graph_tuner_ax_settings(mock_plt, mock_graph_tuner):
    mock_fig = MagicMock()
    mock_ax = MagicMock()
    mock_plt.subplots.return_value = (mock_fig, mock_ax)

    tuner = mock_graph_tuner
    tuner._fig_settings()
    legend_elements = [Patch(facecolor="red", label="test")]
    tuner._ax_settings("ansari", legend_elements, "log")

    mock_ax.set_xscale.assert_called_with("log")
    mock_ax.set_yscale.assert_called_with("log")
    mock_ax.grid.assert_called_once_with(
        True, which="both", ls="--", linewidth=0.5, color="gray", alpha=0.5
    )
    mock_ax.set_xlabel.assert_called_once()
    mock_ax.set_ylabel.assert_called_once()
    mock_ax.set_title.assert_called_once()
    mock_ax.legend.assert_called_once()

    title = mock_ax.set_title.call_args[0][0]
    assert "ansari" in title
    assert "Карта режимов течения" in title

    legend_call = mock_ax.legend.call_args[1]
    assert legend_call["handles"] == legend_elements
    assert legend_call["loc"] == "best"
