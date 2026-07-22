
import math
from data import PipeParams, FluidParams, SystemParams

MEGAPASCAL_TO_PASCAL = 1e6
CELSIUS_TO_KELVIN = 273.15
MM_TO_METRES = 1000.0
GSM3_TO_KGM3 = 1e3

class SIAdapter:
    """
    Адаптер для перевода параметров из общепринятых в нефтегазовой отрасли единиц
    в систему СИ.

    Принимаемые единицы (по умолчанию):
        - diameter_mm: мм          -> м
        - roughness: безразм.      -> без изменений
        - angle_deg: градусы       -> радианы
        - density_liquid, density_gas: кг/м³ (уже СИ, но оставляем)
        - viscosity_liquid, viscosity_gas: Па·с (уже СИ)
        - surface_tension: Н/м     (уже СИ)
        - pressure_MPa: МПа        -> Па
        - temperature_C: °C        -> К
    """
    def __init__(self, diameter: float, roughness: float, angle_deg: float,
                 density_liquid: float, density_gas: float,
                 viscosity_liquid: float, viscosity_gas: float,
                 surface_tension: float, pressure: float, temperature: float):
        self.diameter = diameter
        self.roughness = roughness
        self.angle_deg = angle_deg
        self.density_liquid = density_liquid
        self.density_gas = density_gas
        self.viscosity_liquid = viscosity_liquid
        self.viscosity_gas = viscosity_gas
        self.surface_tension = surface_tension
        self.pressure = pressure
        self.temperature = temperature

    def _diameter_to_m(self) -> float:
        try:
            if self.diameter > 0:
                return self.diameter / MM_TO_METRES
            else:
                return self.diameter
        except TypeError:
            raise TypeError("diameter must be a number")

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

    def _angle_to_rad(self) -> float:
        try:
            return math.radians(self.angle_deg)
        except TypeError:
            raise TypeError("angle_deg must be a number")

    def to_si(self):
        """Возвращает кортеж из трёх датаклассов с параметрами в СИ."""

        pipe = PipeParams(
            diameter=self._diameter_to_m(),
            roughness=self.roughness,
            angle=self._angle_to_rad()
        )
        fluid = FluidParams(
            density_liquid=self.density_liquid,
            density_gas=self.density_gas,
            viscosity_liquid=self.viscosity_liquid,
            viscosity_gas=self.viscosity_gas,
            surface_tension=self.surface_tension
        )
        system = SystemParams(
            pressure=self._pressure_to_pa(),
            temperature=self._temperature_to_k()
        )
        return pipe, fluid, system
