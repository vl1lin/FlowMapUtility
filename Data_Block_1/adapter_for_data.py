import math
from Data_Block_1.data import PipeParams, FluidParams, SystemParams
from typing import Protocol

MEGAPASCAL_TO_PASCAL = 1e6
CELSIUS_TO_KELVIN = 273.15
MM_TO_METRES = 1000.0
GSM3_TO_KGM3 = 1e3

class AdapterProtocol[T](Protocol):
    def to_si(self) -> T:
        ...

class PipeParamsAdapter(AdapterProtocol[PipeParams]):
    def __init__(self, diameter: float, roughness: float, angle: float):
        self.diameter = diameter
        self.roughness = roughness
        self.angle = angle

    def _diameter_to_m(self) -> float:
        """
        Переводит диаметр из мм в метры,
        если диаметр положительный,
        иначе возвращает его без изменений.
        """
        try:
            if self.diameter > 1:
                return self.diameter / MM_TO_METRES
            else:
                return self.diameter
        except TypeError:
            raise TypeError("diameter must be a number")

    def _roughness(self) -> float:
        """
        Проверяет валидный тип данных для шероховатости трубы
        """
        try:
            if self.roughness > 1:
                return self.roughness / MM_TO_METRES
            else:
                return self.roughness
        except TypeError:
            raise TypeError("roughness must be a number")

    def _angle_to_rad(self) -> float:
        """
        Переводит угол в радианы,
        если угол больше 1, иначе возвращает его без изменений.
        """
        try:
            if self.angle > 1:
                return math.radians(self.angle)
            else:
                return self.angle
        except TypeError:
            raise TypeError("angle must be a number")

    def to_si(self) -> PipeParams:
        """
        Переводит параметры трубы в систему СИ.
        return: объект PipeParams
        """
        return PipeParams(
            diameter=self._diameter_to_m(),
            roughness=self._roughness(),
            angle=self._angle_to_rad()
        )

class FluidParamsAdapter(AdapterProtocol[FluidParams]):
    def __init__(self,
        density_liquid: float,
        density_gas: float,
        viscosity_liquid: float,
        viscosity_gas: float,
        surface_tension: float):
        self.density_liquid = density_liquid
        self.density_gas = density_gas
        self.viscosity_liquid = viscosity_liquid
        self.viscosity_gas = viscosity_gas
        self.surface_tension = surface_tension

    def check_valide(self) -> None:
        """
        Проверяет, что все параметры являются числами.
        """
        for param in (
            self.density_liquid, self.density_gas,
            self.viscosity_liquid, self.viscosity_gas,
            self.surface_tension):
            if not isinstance(param, (int, float)):
                raise TypeError(f"{param} must be a number, not {type(param)}")

    def to_si(self) -> FluidParams:
        """
        Переводит параметры потока в систему СИ.
        return: объект FluidParams
        """
        self.check_valide()
        return FluidParams(
            self.density_liquid,
            self.density_gas,
            self.viscosity_liquid,
            self.viscosity_gas,
            self.surface_tension,
        )

class SystemParamsAdapter(AdapterProtocol[SystemParams]):
    def __init__(self, pressure: float, temperature: float):
        self.pressure = pressure
        self.temperature = temperature

    def _pressure_to_pa(self) -> float:
        try:
            if self.pressure < 1000:
                return self.pressure * MEGAPASCAL_TO_PASCAL
            else:
                return self.pressure
        except TypeError:
            raise TypeError("pressure must be a number")

    def _temperature_to_k(self) -> float:
        try:
            if self.temperature < 200:
                return self.temperature + CELSIUS_TO_KELVIN
            else:
                return self.temperature
        except TypeError:
            raise TypeError("temperature must be a number")

    def to_si(self) -> SystemParams:
        """
        Переводит параметры системы в систему СИ.
        return: объект SystemParams
        """
        return SystemParams(
            self._pressure_to_pa(),
            self._temperature_to_k(),
        )
