from unittest.mock import MagicMock, Mock

from flowmaputility.visualization.tuners import ColorTuner


def test_colot_tuner_colormap_settings(mock_mcolors):
    mock_grid = MagicMock()
    mock_ax = MagicMock()
    mock_codes = MagicMock()
    mock_cmap = MagicMock()
    mock_norm = MagicMock()
    mock_mcolors.ListedColormap.return_value = mock_cmap
    mock_mcolors.BoundaryNorm.return_value = mock_norm

    tuner = ColorTuner(mock_ax, mock_grid, mock_codes)
    tuner._colormap_settings([], [])
    assert tuner.cmap == mock_cmap
    assert tuner.norm == mock_norm


def test_color_tuner_create_contur():
    mock_ax = MagicMock()
    mock_grid = MagicMock()
    mock_codes = MagicMock()
    sorted_unique_codes = Mock()
    tuner = ColorTuner(mock_ax, mock_grid, mock_codes)
    tuner.create_countur(sorted_unique_codes)
    mock_ax.contour.assert_called_once_with(
        mock_grid.vsl_2d,
        mock_grid.vsg_2d,
        mock_codes,
        levels=sorted_unique_codes,
        colors="black",
        linewidths=0.8,
    )


def test_color_tuner_drawning_color_grid(mock_color_tuner: ColorTuner, mock_mcolors):
    mock_cmap = MagicMock()
    mock_norm = MagicMock()
    mock_mcolors.ListedColormap.return_value = mock_cmap
    mock_mcolors.BoundaryNorm.return_value = mock_norm
    mock_pc = Mock()
    tuner = mock_color_tuner
    tuner._colormap_settings([], [])
    tuner.ax.pcolormesh.return_value = mock_pc  # type: ignore
    pc = tuner.drawning_color_grid()
    mock_color_tuner.ax.pcolormesh.assert_called_once_with(  # type: ignore
        mock_color_tuner.grid.vsl_2d,
        mock_color_tuner.grid.vsg_2d,
        mock_color_tuner.codes,
        cmap=mock_color_tuner.cmap,
        norm=mock_color_tuner.norm,
        shading="auto",
    )
    assert pc == mock_pc


def test_color_tuner_calling(mock_color_tuner: ColorTuner, mock_mcolors):
    mock_cmap = MagicMock()
    mock_norm = MagicMock()
    mock_mcolors.ListedColormap.return_value = mock_cmap
    mock_mcolors.BoundaryNorm.return_value = mock_norm
    mock_pc = Mock()
    sorted_unique_codes = Mock()
    color = Mock()
    bounds = Mock()
    tuner = mock_color_tuner
    tuner.ax.pcolormesh.return_value = mock_pc  # type: ignore
    pc = tuner(color, bounds, sorted_unique_codes)
    mock_mcolors.ListedColormap.assert_called_once_with(color)
    mock_mcolors.BoundaryNorm.assert_called_once_with(bounds, mock_cmap.N)
    tuner.ax.contour.assert_called_once_with(  # type: ignore
        mock_color_tuner.grid.vsl_2d,
        mock_color_tuner.grid.vsg_2d,
        mock_color_tuner.codes,
        levels=sorted_unique_codes,
        colors="black",
        linewidths=0.8,
    )
    mock_color_tuner.ax.pcolormesh.assert_called_once_with(  # type: ignore
        mock_color_tuner.grid.vsl_2d,
        mock_color_tuner.grid.vsg_2d,
        mock_color_tuner.codes,
        cmap=mock_color_tuner.cmap,
        norm=mock_color_tuner.norm,
        shading="auto",
    )
    assert pc == mock_pc
