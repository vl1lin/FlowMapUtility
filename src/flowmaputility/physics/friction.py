import math
from typing import Final

_LAMINAR_MAX_REYNOLDS: Final = 2000.0  # Граница ламинарного режима течения в трубе
_LAMINAR_COEFFICIENT: Final = 64.0  # f = 64 / Re (Дарси–Вейсбах)

# Коэффициенты явной аппроксимации Брькича (2011) уравнения Колбрука
_BRKIC_INNER_COEFFICIENT: Final = 1.816
_BRKIC_LOG_COEFFICIENT: Final = 1.1
_COLEBROOK_ROUGHNESS_DIVISOR: Final = 3.71
_COLEBROOK_SLOPE: Final = 2.0


def darcy_friction_factor(reynolds: float, relative_roughness: float) -> float:
    """
    Коэффициент трения Дарси–Вейсбаха (диаграмма Муди).

    Ламинарный режим (Re < 2000): f = 64 / Re.
    Турбулентный режим: явная аппроксимация Брькича уравнения Колбрука.

    :param reynolds: число Рейнольдса, безразмерное, должно быть > 0
    :param relative_roughness: относительная шероховатость ε/d, безразмерная
    :return: коэффициент трения Дарси, безразмерный
    :raises ValueError: если число Рейнольдса не положительное
    """
    if not reynolds > 0.0:
        raise ValueError(f"Число Рейнольдса должно быть > 0, получено {reynolds}")
    if reynolds < _LAMINAR_MAX_REYNOLDS:
        return _LAMINAR_COEFFICIENT / reynolds

    inner = _BRKIC_LOG_COEFFICIENT * reynolds
    s = math.log(
        reynolds / (_BRKIC_INNER_COEFFICIENT * math.log(inner / math.log(1.0 + inner)))
    )
    root_term = -_COLEBROOK_SLOPE * math.log10(
        relative_roughness / _COLEBROOK_ROUGHNESS_DIVISOR
        + _COLEBROOK_SLOPE * s / reynolds
    )
    return 1.0 / root_term**2
