import math
from typing import Protocol

from Data_Block_1.data import FluidParams, PipeParams, SystemParams

MEGAPASCAL_TO_PASCAL = 1e6
CELSIUS_TO_KELVIN = 273.15
MM_TO_METRES = 1000.0
GSM3_TO_KGM3 = 1e3


class AdapterProtocol[T](Protocol):
    def to_si(self) -> T: ...


class PipeParamsAdapter(AdapterProtocol[PipeParams]):
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

    def to_si(self) -> PipeParams:
        """
        Переводит параметры трубы в систему СИ.
        return: объект PipeParams
        """
        return PipeParams(
            diameter=self._diameter_to_m(),
            roughness=self._roughness(),
            angle=self._angle_to_rad(),
        )

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
        Проверяет валидный тип данных для угла наклона трубы и возвращает его в градусах
        """
        try:
            if self.angle > 1:
                return float(self.angle)
            else:
                return float(self.angle) * 180 / math.pi
        except TypeError:
            raise TypeError("angle must be a number")


class FluidParamsAdapter(AdapterProtocol[FluidParams]):
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

    def to_si(self) -> FluidParams:
        """
        Переводит параметры потока в систему СИ.
        return: объект FluidParams
        """
        return FluidParams(
            density_liquid=self._density_to_si(self.density_liquid),
            density_gas=self._density_to_si(self.density_gas),
            viscosity_liquid=self._viscosity_to_si(self.viscosity_liquid),
            viscosity_gas=self._viscosity_to_si(self.viscosity_gas),
            surface_tension=self._surface_tension_to_si(self.surface_tension),
        )

    def _density_to_si(self, density: float) -> float:
        """
        Проверяет валидность плотности и конвертирует в систему СИ.
        г/см³ -> кг/м³
        :param density: плотность
        """
        try:
            if density <= 1:
                return density * 1000.0
            else:
                return density
        except TypeError:
            raise TypeError(f"density must be a number, not {type(density)}")

    def _viscosity_to_si(self, viscosity: float) -> float:
        """
        Проверяет валидность вязкости и конвертирует в систему СИ.
        :param viscosity: вязкость
        сПз -> Па*с
        """
        try:
            if viscosity >= 1:
                return viscosity / 1000.0
            else:
                return viscosity
        except TypeError:
            raise TypeError(f"viscosity must be a number, not {type(viscosity)}")

    def _surface_tension_to_si(self, surface_tension: float) -> float:
        """
        Конвертирует поверхностное натяжение в систему СИ.
        :param surface_tension: поверхностное натажение на границе жидкость-газ
        мН/м -> Н/м
        """
        try:
            if surface_tension >= 1:
                return surface_tension / 1000.0
            else:
                return surface_tension
        except TypeError:
            raise TypeError(
                f"surface_tension must be a number, not {type(surface_tension)}"
            )


class SystemParamsAdapter(AdapterProtocol[SystemParams]):
    """
    Адаптер для SystemParams.
    Принимает извне данные, конвертирует в СИ и возвращает объект SystemParams.
    :param pressure: давление: Па или МПа
    :param temperature: температура: К или градусы
    """

    def __init__(self, pressure: float, temperature: float):
        self.pressure = pressure
        self.temperature = temperature

    def to_si(self) -> SystemParams:
        """
        Переводит параметры системы в систему СИ.
        return: объект SystemParams
        """
        return SystemParams(
            self._pressure_to_pa(),
            self._temperature_to_k(),
        )

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
