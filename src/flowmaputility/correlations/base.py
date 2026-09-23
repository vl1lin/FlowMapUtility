import math
from abc import ABC, abstractmethod
from enum import IntEnum

from flowmaputility.domain.params import FluidParams, PipeParams


class FlowPatternCode(IntEnum):
    """Единый словарь режимов для всех корреляций"""

    SINGLE_LIQUID = 100
    SINGLE_GAS = 101
    BUBBLE = 102
    SLUG = 103
    DISPERSED_BUBBLE = 104
    ANNULAR = 105
    STRATIFIED = 106  # Добавим для горизонтальных труб
    STRATIFIED_WAVY = 107  # Расслоённый волновой
    CHURN = 108  # Эмульсионный (churn)
    UNKNOWN = 199


class IFlowModel(ABC):
    """
    Базовый интерфейс для всех моделей корреляции
    :param pipe: Объект PipeParams, в котором информация о трубе
    :param fluid: Объект FluidParams, в котором информация о свойствах флюидов в потоке
    """

    def __init__(self, pipe: PipeParams, fluid: FluidParams):
        self.pipe = pipe
        self.fluid = fluid

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Человеческое имя модели для логов и графиков"""
        ...

    @classmethod
    @abstractmethod
    def angle_limit(cls) -> tuple[float, float]:
        """Допустимый диапазон углов в градусах (min, max)"""
        ...

    @abstractmethod
    def get_pattern_code(self, vsl: float, vsg: float) -> int:
        """
        Вычислить режим течения для одной точки.
        :param vsl: скорость жидкости
        :param vsg: скорость газа
        :return: код режима течения из Enum FlowPattern
        """
        ...

    def validate_angle(self) -> None:
        """
        Валидировать угол течения.
        :raises ValueError: если угол выходит за допустимый диапазон
        """
        min, max = self.angle_limit()
        if self.pipe.angle < min or self.pipe.angle > max:
            raise ValueError(
                f"Модель '{self.name()}' работает только для углов"
                f"{min}°-{max}°.\nТекущий угол: {self.pipe.angle}°"
            )

    def _friction_factor(self, n_re: float, roughness_d: float) -> float:
        """
        Moody (Darcy-Weisbach) friction factor using Brkic explicit approximation.

        Laminar: f = 64/Re. Turbulent: Brkic (2011) approximation of Colebrook.

        :param n_re: Reynolds number. Type: float
        :param roughness_d: relative pipe roughness (eps/d). Type: float
        :return: Darcy friction factor. Type: float
        """
        if n_re == 0.0:
            return 0.0
        if n_re < 2000.0:
            return 64.0 / n_re
        # Brkic explicit approximation (case 3 in VBA)
        s = math.log(n_re / (1.816 * math.log(1.1 * n_re / math.log(1.0 + 1.1 * n_re))))
        f1 = -2.0 * math.log10(roughness_d / 3.71 + 2.0 * s / n_re)
        return 1.0 / f1**2
