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
    def generate(self) -> GridInfo:
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


    def generate(self) -> GridInfo:
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

        vsl_1d = self._generate_1d_array(vsl_min, vsl_max)
        vsg_1d = self._generate_1d_array(vsg_min, vsg_max)

        vsl_2d = self._generate_2d_array_x(vsl_1d)
        vsg_2d = self._generate_2d_array_y(vsg_1d)

        return GridInfo(vsl_1d, vsg_1d, vsl_2d, vsg_2d, self.resolution, self.log_scale)

    def _generate_1d_array(self, min_val: float, max_val: float) -> np.ndarray:
        """
        Генерирует одномерный массив значений от min_val до max_val с заданным разрешением.

        :param min_val: Минимальное значение.
        :param max_val: Максимальное значение.
        :return: Одномерный массив значений.
        """
        if self.log_scale:

            vsl_1d = np.logspace(min_val, max_val, self.resolution)
        else:

            vsl_1d = np.linspace(min_val, max_val, self.resolution)

        return vsl_1d

    def _generate_2d_array_x(self, vsl_1d: np.ndarray) -> np.ndarray:
        """
        Генерирует двумерный массив, повторяя строки.

        :param vsl_1d: Одномерный массив значений.
        :return: Двумерный массив, повторяющий vsl_1d по оси x.
        """
        vsl_2d = np.ones((self.resolution, 1)) * vsl_1d
        return vsl_2d

    def _generate_2d_array_y(self, vsg_1d: np.ndarray) -> np.ndarray:
        """
        Генерирует двумерный массив, разворачивая одномерный массив и повторяя столбцы.

        :param vsg_1d: Одномерный массив значений.
        :return: Двумерный массив, повторяющий vsg_1d по оси y.
        """
        revese_vsg_1d = np.flip(vsg_1d)
        vsg_2d = revese_vsg_1d[:, np.newaxis] * np.ones(self.resolution)
        return vsg_2d

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
