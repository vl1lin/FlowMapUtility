from Grid_Generation.grid_info import GridInfo

import warnings

import numpy as np

from abc import ABC, abstractmethod

from typing import cast


class GridGeneratorABS(ABC):
    """
    Класс GridGenerator управляет генерацией сетки.

    Attributes:
        vsl_range: Диапазон скоростей жидкости.
        vsg_range: Диапазон скоростей газа.
        resolution: Разрешение сетки.
        log_scale: Флаг, указывающий на использование логарифмической шкалы.
    """

    def __init__(self,
        vsl_range: tuple[float, float],
        vsg_range: tuple[float, float],
        resolution: int = 100,
        log_scale: bool = True):
        self.vsl_range: tuple[float, float] = vsl_range
        self.vsg_range: tuple[float, float] = vsg_range
        self.resolution: int = resolution
        self.log_scale: bool = log_scale

    @abstractmethod
    def grid_generator(self) -> GridInfo:
        """
        Генерирует сетку и возвращает информацию о ней.
        :return: Объект GridInfo с информацией о сетке.
        """
        pass

class GridGenerator(GridGeneratorABS):

    def __init__(self,
        vsl_range: tuple[float, float],
        vsg_range: tuple[float, float],
        resolution: int = 100,
        log_scale: bool = True):
        super().__init__(vsl_range, vsg_range, resolution, log_scale)


    def grid_generator(self) -> GridInfo:
        """
        Генерирует сетку и возвращает информацию о ней.
        :return: Объект GridInfo с информацией о сетке.
        """
        self.validation_befor_grid_generation()

        vsl_min, vsl_max = self.vsl_range
        vsg_min, vsg_max = self.vsg_range

        if vsl_min <= 0 or vsg_min <= 0:
            warnings.warn("log_scale requires positive values, switching to linear scale")
            self.log_scale = False

        if self.log_scale:

            vsl_1d = np.logspace(vsl_min, vsl_max, self.resolution)
            vsg_1d = np.logspace(vsg_min, vsg_max, self.resolution)

        else:

            vsl_1d = np.linspace(vsl_min, vsl_max, self.resolution)
            vsg_1d = np.linspace(vsg_min, vsg_max, self.resolution)

        vsl_2d, vsg_2d = np.meshgrid(vsl_1d, vsg_1d, indexing='ij')
        return GridInfo(vsl_1d, vsg_1d, vsl_2d, vsg_2d, self.resolution)

    def validation_befor_grid_generation(self) -> None:
        """
        Выполняет валидацию параметров перед генерацией сетки.
        Изменяет значения атрибутов на основе валидации.
        """
        self.vsl_range = self._validation_range(self.vsl_range)
        self.vsg_range = self._validation_range(self.vsg_range)

        try:
            self.resolution = int(self.resolution)
        except (TypeError, ValueError) as e:
            e.add_note(f"resolution must be a number, got {self.resolution}")
            raise e

        if not isinstance(self.log_scale, bool):
            raise TypeError("log_scale must be a boolean")

    def _validation_range(self, range_input: tuple[float, float]) -> tuple[float, float]:
        """
        Валидирует диапазон значений скорости.
        :param range_input: Кортеж с минимальным и максимальным значением скорости
        """
        if len(range_input) != 2:
            raise ValueError("range_input must be a tuple of two numbers")
        try:
            vs = tuple(float(i) for i in range_input)
        except (IndexError, ValueError, TypeError) as e:
            e.add_note(f"Диапазон должен быть кортежем из двух чисел. Получено: {range_input}")
            raise e

        if vs[0] > vs[1]:
            warnings.warn(f"Минимальное значение ({vs[0]}) должно быть строго меньше максимального ({vs[1]}) \n Меняем местами")
            vs = (vs[1], vs[0])

        return cast(tuple[float, float], vs)
