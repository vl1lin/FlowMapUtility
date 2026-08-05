from typing import Protocol

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from matplotlib.collections import QuadMesh

from Grid_Generation.grid_info import GridInfo
from visualization.map_info import DEFAULT_COLORS, PATTERN_NAMES



class ColorTuner:
    """
    Настройщик цветовой карты
    :param ax: Ось для отрисовки
    :param grid: Информация о сетке (объект GridInfo)
    :param codes: Матрица кодов (неотсортированная)
    :param cmap: Цветовая карта (не передается извне)
    :param norm: Нормализация цветовой карты (не передается извне)
    """
    def __init__(self, ax: Axes, grid: GridInfo, codes: np.ndarray) -> None:
        self.ax = ax
        self.grid = grid
        self.codes = codes
        self.cmap: mcolors.ListedColormap
        self.norm: mcolors.BoundaryNorm

    def __call__(self, colors: list[str], bounds: list[float], sorted_unique_codes: np.ndarray) -> QuadMesh:
        """
        Вызов настроек цветовой карты и отрисовки сетки
        :param colors: Список цветов
        :param bounds: Список границ
        :param sorted_unique_codes: Уникальные коды, отсортированные по возрастанию
        :return: Объект QuadMesh
        """
        self._colormap_settings(colors, bounds)
        self.create_countur(sorted_unique_codes)
        pc = self.drawning_color_grid()
        return pc

    def drawning_color_grid(self) -> QuadMesh:
        """
        Отрисовка цветовой сетки на основе кодов.
        :return: Объект QuadMesh
        """
        pc = self.ax.pcolormesh(
                self.grid.vsl_2d, self.grid.vsg_2d, self.codes,
                cmap=self.cmap, norm=self.norm,
                shading='auto'
            )
        return pc

    def _colormap_settings(self, colors: list[str], bounds: list[float]) -> None:
        """
        Установка цветовой карты и нормализации на основе цветов и границ.
        :param colors: Список цветов
        :param bounds: Список границ
        """
        self.cmap = mcolors.ListedColormap(colors)
        self.norm = mcolors.BoundaryNorm(bounds, self.cmap.N)

    def create_countur(self, sorted_unique_codes: np.ndarray) -> None:
        """
        Создание контура на основе отсортированных уникальных кодов.
        :param sorted_unique_codes: Отсортированный массив уникальных кодов
        """
        self.ax.contour(
                self.grid.vsl_2d, self.grid.vsg_2d, self.codes,
                levels=sorted_unique_codes,
                colors='black',
                linewidths=0.8
            )




class GraphTuner:
    """
    Настройщик графика для визуализации
    :param fig: Объект Figure (создается внутри)
    :param ax: Объект Axes (создается внутри)
    """
    def __init__(self):
        self.fig: Figure
        self.ax: Axes

    def __call__(self, model_name: str, codes: np.ndarray, log_scale: bool) -> tuple[Figure, Axes]:
        """
        Вызов создания осей и фигуры для графика а также их настройка
        :param model_name: Название модели
        :param codes: Массив кодов
        :param log_scale: Флаг, указывающий на использование логарифмической шкалы
        :return: Объект Figure и Axes
        """
        self._fig_settings()
        scale = self.set_scale(log_scale)
        legend_elements = self._create_legend(codes)
        self._ax_settings(model_name, legend_elements, scale)
        return self.fig, self.ax

    def _fig_settings(self) -> None:
        """
        Настройка фигуры и осей
        """
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.fig.patch.set_facecolor("white")

    @classmethod
    def set_scale(cls, log_scale: bool) -> str:
        """
        Установка типа шкалы (логарифмическая или линейная)
        :param log_scale: Флаг, указывающий на использование логарифмической шкалы
        :return: Тип шкалы ('log' или 'linear')
        """
        scale_type = 'log' if log_scale else 'linear'
        return scale_type

    def _ax_settings(self, model_name: str, legend_elements: list[Patch], scale: str) -> None:
        """
        Настройка осей графика
        :param model_name: Название модели
        :param legend_elements: Список элементов легенды
        :param scale: Тип шкалы ('log' или 'linear')
        """
        self.ax.set_xscale(scale)
        self.ax.set_yscale(scale)
        self.ax.grid(True, which="both", ls="--", linewidth=0.5, color='gray', alpha=0.5)
        self.ax.set_xlabel('Приведенная скорость жидкости ($v_{sl}$), м/с', fontsize=12)
        self.ax.set_ylabel('Приведенная скорость газа ($v_{sg}$), м/с', fontsize=12)
        self.ax.set_title(f'Карта режимов течения \n Расчетная модель: {model_name}', fontsize=14, pad=15)
        self.ax.legend(handles=legend_elements, loc='best', framealpha=0.9)

    @classmethod
    def _create_legend(cls, sorted_unique_codes: np.ndarray) -> list[Patch]:
        """
        Создание элементов легенды
        :param sorted_unique_codes: Уникальные коды, отсортированные по возрастанию
        :return: Список элементов легенды
        """
        legend_elements = []
        for code in sorted_unique_codes:
            color = DEFAULT_COLORS.get(code, '#FFFFFF')
            name = PATTERN_NAMES.get(code, f'Код {code}')
            # Создаем закрашенный квадратик для легенды
            patch = Patch(facecolor=color, edgecolor='black', label=name)
            legend_elements.append(patch)
        return legend_elements
