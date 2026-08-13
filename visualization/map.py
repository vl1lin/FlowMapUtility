from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

from visualization.map_info import DEFAULT_COLORS, PATTERN_NAMES
from visualization.tuners import ColorTuner, GraphTuner

if TYPE_CHECKING:
    from Grid_Generation.grid_info import GridInfo


class MapVisualizer:
    """
    Менеджер визуализации карты
    :param code_matrix: Матрица кодов (неотсортированная)
    :param grid: Информация о сетке (объект GridInfo)
    :param show_plot: Показывать ли график (флаг)
    :param save_path: Путь для сохранения графика
    """

    def __init__(
        self,
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
        """
        Основной метод для запуска визуализации карты
        """
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
        """
        Возвращает уникальные коды паттернов в отсортированном порядке
        :return: Отсортированный массив NumPy уникальных кодов
        """
        unique_codes = np.unique(self.codes)
        sorted_codes = np.sort(unique_codes)
        return sorted_codes

    @classmethod
    def _get_colors(cls, sorted_unique_codes: np.ndarray) -> list[str]:
        """
        Возвращает список цветов для уникальных кодов паттернов
        :param sorted_unique_codes: Отсортированный массив NumPy уникальных кодов
        :return: Список цветов
        """
        pattern_colors = [
            DEFAULT_COLORS.get(code, "#FFFFFF") for code in sorted_unique_codes
        ]
        return pattern_colors

    @classmethod
    def _get_pattern_names(cls, sorted_unique_codes: np.ndarray) -> list[str]:
        """
        Возвращает список названий паттернов для уникальных кодов
        :param sorted_unique_codes: Отсортированный массив NumPy уникальных кодов
        :return: Список названий
        """
        pattern_names = [
            PATTERN_NAMES.get(code, "Такой код не предусмотрен")
            for code in sorted_unique_codes
        ]
        return pattern_names

    @classmethod
    def _create_color_bounds(cls, sorted_codes: np.ndarray) -> list[float]:
        """
        Возвращает список границ для цветовых палитр
        :param sorted_codes: Отсортированный массив NumPy уникальных кодов
        :return: Список границ
        """
        bounds = [c - 0.5 for c in sorted_codes] + [sorted_codes[-1] + 0.5]
        return bounds

    @classmethod
    def _save_map(cls, save_path: str | None) -> None:
        """
        Сохраняет карту в файл
        :param save_path: Путь для сохранения
        """
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Карта сохранена в {save_path}")

    @classmethod
    def _show_map(cls, show_plot: bool) -> None:
        """
        Отображает карту
        :param show_plot: Показать ли график (флаг)
        """
        if show_plot:
            plt.show()
        else:
            plt.close()
