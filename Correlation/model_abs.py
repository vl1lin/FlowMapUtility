from abc import ABC, abstractmethod
from enum import IntEnum
from Data_Block_1.data import PipeParams, FluidParams

class FlowPatternCode(IntEnum):
    """Единый словарь режимов для всех корреляций"""
    SINGLE_LIQUID = 100
    SINGLE_GAS = 101
    BUBBLE = 102
    SLUG = 103
    DISPERSED_BUBBLE = 104
    ANNULAR = 105
    STRATIFIED = 106 # Добавим для горизонтальных труб
    UNKNOWN = 199

class IFlowModel(ABC):
    """
    Базовый интерфейс для всех моделей корреляции<[fim-middle]>
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
                f"Модель '{self.name}' работает только для углов"
                f"{min}°-{max}°.\nТекущий угол: {self.pipe.angle}°"
            )
