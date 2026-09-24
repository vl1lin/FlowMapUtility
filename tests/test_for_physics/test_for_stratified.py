import math
from typing import TypedDict

import numpy as np
import pytest

from flowmaputility.physics import stratified
from flowmaputility.physics.stratified import (
    EquilibriumLevel,
    kelvin_helmholtz_gas_velocity,
    least_residual_level,
    solve_equilibrium_level,
    stratified_geometry,
    stratified_residual,
)


class _Args(TypedDict):
    """Аргументы `solve_equilibrium_level` (типизированный набор для распаковки `**`)."""

    superficial_liquid_velocity: float
    superficial_gas_velocity: float
    diameter: float
    liquid_density: float
    gas_density: float
    liquid_viscosity: float
    gas_viscosity: float
    angle_rad: float


def _args(vsl: float, vsg: float, angle_rad: float) -> _Args:
    """Вода–воздух, d = 0.05 м."""
    return {
        "superficial_liquid_velocity": vsl,
        "superficial_gas_velocity": vsg,
        "diameter": 0.05,
        "liquid_density": 1000.0,
        "gas_density": 1.2,
        "liquid_viscosity": 1e-3,
        "gas_viscosity": 1.8e-5,
        "angle_rad": angle_rad,
    }


def _solve(angle_deg: float, vsl: float = 0.01, vsg: float = 1.0) -> EquilibriumLevel:
    return solve_equilibrium_level(**_args(vsl, vsg, math.radians(angle_deg)))


# --- Геометрия -------------------------------------------------------------


@pytest.mark.parametrize("level", [0.1, 0.3, 0.5, 0.7, 0.9])
def test_areas_sum_to_pipe_area(level: float):
    geometry = stratified_geometry(level)
    assert geometry.liquid_area + geometry.gas_area == pytest.approx(
        math.pi / 4.0, abs=1e-12
    )
    assert geometry.liquid_perimeter + geometry.gas_perimeter == pytest.approx(
        math.pi, abs=1e-12
    )


def test_half_filled_pipe_geometry():
    geometry = stratified_geometry(0.5)
    assert geometry.liquid_area == pytest.approx(math.pi / 8.0, abs=1e-12)
    assert geometry.liquid_perimeter == pytest.approx(math.pi / 2.0, abs=1e-12)
    assert geometry.interface_width == pytest.approx(1.0, abs=1e-12)


def test_liquid_area_grows_with_level():
    areas = [
        stratified_geometry(level).liquid_area for level in np.linspace(0.05, 0.95, 19)
    ]
    assert areas == sorted(areas)


@pytest.mark.parametrize("level", [0.0, 1.0, -0.1, 1.5])
def test_geometry_invalid_level(level: float):
    with pytest.raises(ValueError):
        stratified_geometry(level)


# --- Равновесный уровень ---------------------------------------------------


def test_horizontal_level():
    result = _solve(0.0)
    assert result.level == pytest.approx(0.262, rel=0.02)
    assert len(result.all_roots) == 1


def test_upflow_level():
    assert _solve(5.0).level == pytest.approx(0.895, rel=0.03)


def test_level_sign_of_gravity_term():
    """Восходящий поток — выше уровень жидкости: h(−5°) < h(0°) < h(+5°)."""
    downflow, horizontal, upflow = (_solve(a).level for a in (-5.0, 0.0, 5.0))
    assert downflow is not None and horizontal is not None and upflow is not None
    assert downflow < horizontal < upflow


def test_level_satisfies_equation():
    level = _solve(0.0).level
    assert level is not None
    residual = stratified_residual(level=level, **_args(0.01, 1.0, 0.0))
    assert abs(residual) < 1e-6


def test_multiple_roots_smallest_is_taken():
    result = _solve(45.0, vsl=0.001, vsg=50.0)
    assert len(result.all_roots) == 3
    assert list(result.all_roots) == sorted(result.all_roots)
    assert result.level == result.all_roots[0]


def test_no_root_returns_none_and_least_residual_level_is_on_grid(monkeypatch):
    def positive_residual(**_: float) -> np.ndarray:
        return np.linspace(2.0, 1.0, stratified._LEVEL_GRID.size)

    monkeypatch.setattr(stratified, "_stratified_residual_grid", positive_residual)
    kwargs = _args(0.3, 2.0, 0.0)
    assert solve_equilibrium_level(**kwargs) == EquilibriumLevel(None, ())
    assert least_residual_level(**kwargs) == pytest.approx(1.0 - 1e-4)


def test_grid_residual_matches_scalar_residual():
    kwargs = _args(0.3, 2.0, math.radians(-7.0))
    grid_values = stratified._stratified_residual_grid(**kwargs)
    for index in (0, 57, 200, 333, 400):
        level = float(stratified._LEVEL_GRID[index])
        scalar = stratified_residual(level=level, **kwargs)
        assert grid_values[index] == pytest.approx(scalar, rel=1e-9)


# --- Критерий Кельвина–Гельмгольца -----------------------------------------


def test_kelvin_helmholtz_velocity_is_positive_and_scales_with_level():
    low = kelvin_helmholtz_gas_velocity(
        geometry=stratified_geometry(0.2),
        diameter=0.05,
        liquid_density=1000.0,
        gas_density=1.2,
        angle_rad=0.0,
    )
    high = kelvin_helmholtz_gas_velocity(
        geometry=stratified_geometry(0.8),
        diameter=0.05,
        liquid_density=1000.0,
        gas_density=1.2,
        angle_rad=0.0,
    )
    assert low > high > 0.0
