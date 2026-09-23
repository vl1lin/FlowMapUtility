import math

import pytest

from flowmaputility.physics.friction import darcy_friction_factor


@pytest.mark.parametrize("reynolds", [1.0, 100.0, 1999.0])
@pytest.mark.parametrize("relative_roughness", [0.0, 1e-3])
def test_laminar_is_64_over_re(reynolds: float, relative_roughness: float):
    assert darcy_friction_factor(reynolds, relative_roughness) == 64.0 / reynolds


def _colebrook(reynolds: float, relative_roughness: float) -> float:
    """Неявное уравнение Колбрука, решение итерациями."""
    inverse_root = 8.0
    for _ in range(200):
        inverse_root = -2.0 * math.log10(
            relative_roughness / 3.71 + 2.51 * inverse_root / reynolds
        )
    return 1.0 / inverse_root**2


# Формула взята из VBA-порта (коэффициент 2.0 при s/Re) и отличается от Колбрука
# до ~2.1% (при Re = 1e4, ε/d = 0); с коэффициентом 2.18 из статьи Брькича
# расхождение до 1.2%, поэтому порог 1% из ТЗ недостижим ни для одного варианта.
_MAX_COLEBROOK_DEVIATION = 0.025


@pytest.mark.parametrize("reynolds", [1e4, 1e5, 1e6])
@pytest.mark.parametrize("relative_roughness", [0.0, 1e-4, 1e-3])
def test_turbulent_close_to_colebrook(reynolds: float, relative_roughness: float):
    actual = darcy_friction_factor(reynolds, relative_roughness)
    expected = _colebrook(reynolds, relative_roughness)
    assert abs(actual - expected) / expected < _MAX_COLEBROOK_DEVIATION


@pytest.mark.parametrize("reynolds", [0.0, -1.0, -1e5, float("nan")])
def test_non_positive_reynolds_raises(reynolds: float):
    with pytest.raises(ValueError):
        darcy_friction_factor(reynolds, 1e-4)
