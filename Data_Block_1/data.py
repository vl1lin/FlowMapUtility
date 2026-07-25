from dataclasses import dataclass

"""
Классы содержащие исходные данные, которые будут задаваться извне
"""

@dataclass(frozen=True)
class PipeParams:
    """
    Параметры трубы

    Attributes
    ---------
    diameter: float
        Диаметр сечения трубы: м
    roughness: float
        Шероховатость трубы: м
    angle: float
        Угол наклона трубы: градусы
    """

    diameter: float
    roughness: float
    angle: float


@dataclass(frozen=True)
class FluidParams:
    """

    Параметры флюида (газожидкостной смеси)

    Attributes

    ---------

    density_liquid: float
        Плотность жидкости: кг/м^3
    density_gas: float
        Плотность газа: кг/м^3
    viscosity_liquid: float
        Вязкость жидкости: Па * с
    viscosity_gas: float
        Вязкость газа: Па * с
    surface_tension: float
        Поверхностное натяжение: Н/м

    """

    density_liquid: float
    density_gas: float
    viscosity_liquid: float
    viscosity_gas: float
    surface_tension: float


@dataclass(frozen=True)
class SystemParams:
    """

    Параметры системы

    Attributes

    ---------

    pressure: float
        Дааление: Па
    temperature: float
        Температура: К

    """

    pressure: float
    temperature: float
