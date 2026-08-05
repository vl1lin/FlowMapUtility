from typing import TYPE_CHECKING
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from visualization.tuners import GraphTuner, ColorTuner
from visualization.map_info import DEFAULT_COLORS, PATTERN_NAMES

if TYPE_CHECKING:
    from Grid_Generation.grid_info import GridInfo

class MapVisualizer:
    def __init__(self,
        code_matrix: np.ndarray,
        grid: "GridInfo",
        show_plot: bool = True,
        save_path: str | None = None,
    ):
        self.codes = code_matrix
        self.grid = grid
        self.show_plot = show_plot
        self.save_path = save_path
        self.graph_tuner = GraphTuner()
        self.color_tuner: ColorTuner

    def run(self):
        unique_codes = self._get_unique_patterns()
        pattern_colors = self._get_colors(unique_codes)
        pattern_names = self._get_pattern_names(unique_codes)
        fig, ax = self.graph_tuner("", unique_codes, self.grid.log_scale)
        self.color_tuner = ColorTuner(ax, self.grid, self.codes)
        color_bounds = self._create_color_bounds(unique_codes)
        map = self.color_tuner(pattern_colors, color_bounds, unique_codes)
        self._save_map(self.save_path)
        self._show_map(self.show_plot)


    def _get_unique_patterns(self) -> np.ndarray:
        unique_codes = np.unique(self.codes)
        sorted_codes = np.sort(unique_codes)
        return sorted_codes

    @classmethod
    def _get_colors(cls, sorted_unique_codes: np.ndarray) -> list[str]:
        pattern_colors = [DEFAULT_COLORS.get(code, '#FFFFFF') for code in sorted_unique_codes]
        return pattern_colors

    @classmethod
    def _get_pattern_names(cls, sorted_unique_codes: np.ndarray) -> list[str]:
        pattern_names = [PATTERN_NAMES.get(code, "Такой код не предусмотрен") for code in sorted_unique_codes]
        return pattern_names

    @classmethod
    def _create_color_bounds(cls, sorted_codes: np.ndarray) -> list[float]:
        bounds = [c - 0.5 for c in sorted_codes] + [sorted_codes[-1] + 0.5]
        return bounds


    @classmethod
    def _save_map(cls, save_path: str | None):
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Карта сохранена в {save_path}")

    @classmethod
    def _show_map(cls, show_plot: bool):
        if show_plot:
            plt.show()
        else:
            plt.close()
