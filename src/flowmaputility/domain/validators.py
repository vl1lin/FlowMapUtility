from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from flowmaputility.domain.params import FluidParams, PipeParams, SystemParams

MEGAPASCAL_TO_PASCAL = 1e6
CELSIUS_TO_KELVIN = 273.15
MM_TO_METRES = 1000.0
GSM3_TO_KGM3 = 1e3

T = TypeVar("T")


class BaseValidator(ABC, Generic[T]):
    def __init__(self):
        self._validate()

    def _validate(self) -> None:
        for param, value in vars(self).items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"{param} must be number")
            setattr(self, param, float(value))

    @abstractmethod
    def validate(self) -> T: ...


class PipeParamsValidator(BaseValidator[PipeParams]):
    """
    Адаптер для PipeParams.
    Принимает извне данные, конвертирует в СИ и возвращает объект PipeParams.
    :param diameter: диаметр сечения трубы: мм или м
    :param roughness: шероховатость трубы: мм или м
    :param angle: угол наклона трубы: градусы или радианы
    """

    def __init__(self, diameter: float, roughness: float, angle: float):
        self.diameter = diameter
        self.roughness = roughness
        self.angle = angle
        super().__init__()

    def validate(self) -> PipeParams:
        return PipeParams(
            diameter=self.diameter,
            roughness=self.roughness,
            angle=self.angle,
        )


class FluidParamsValidator(BaseValidator[FluidParams]):
    """
    Адаптер для FluidParams.
    Принимает извне данные, конвертирует в СИ и возвращает объект FluidParams.
    :param density_liquid: плотность жидкости: кг/м³
    :param density_gas: плотность газа: кг/м³
    :param viscosity_liquid: вязкость жидкости: Па·с
    :param viscosity_gas: вязкость газа: Па·с
    :param surface_tension: поверхностная плотность: Н/м
    """

    def __init__(
        self,
        density_liquid: float,
        density_gas: float,
        viscosity_liquid: float,
        viscosity_gas: float,
        surface_tension: float,
    ):
        self.density_liquid = density_liquid
        self.density_gas = density_gas
        self.viscosity_liquid = viscosity_liquid
        self.viscosity_gas = viscosity_gas
        self.surface_tension = surface_tension
        super().__init__()

    def validate(self) -> FluidParams:
        return FluidParams(
            density_liquid=self.density_liquid,
            density_gas=self.density_gas,
            viscosity_liquid=self.viscosity_liquid,
            viscosity_gas=self.viscosity_gas,
            surface_tension=self.surface_tension,
        )


class SystemParamsValidator(BaseValidator[SystemParams]):
    """
    Адаптер для SystemParams.
    Принимает извне данные, конвертирует в СИ и возвращает объект SystemParams.
    :param pressure: давление: Па или МПа
    :param temperature: температура: К или градусы
    """

    def __init__(self, pressure: float, temperature: float):
        self.pressure = pressure
        self.temperature = temperature
        super().__init__()

    def validate(self) -> SystemParams:
        return SystemParams(pressure=self.pressure, temperature=self.temperature)
