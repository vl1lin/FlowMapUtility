import time

import pytest

from flowmaputility.correlations import taitel_dukler
from flowmaputility.correlations.base import FlowPatternCode
from flowmaputility.correlations.taitel_dukler import (
    TaitelDuklerModel,
    TaitelDuklerReason,
    TaitelDuklerResult,
    TaitelDuklerSettings,
)
from flowmaputility.domain.params import FluidParams, PipeParams
from flowmaputility.physics.stratified import EquilibriumLevel

_STRATIFIED = FlowPatternCode.STRATIFIED
_WAVY = FlowPatternCode.STRATIFIED_WAVY
_SLUG = FlowPatternCode.SLUG
_DISPERSED = FlowPatternCode.DISPERSED_BUBBLE
_ANNULAR = FlowPatternCode.ANNULAR

_WATER_AIR = FluidParams(
    density_liquid=1000.0,
    density_gas=1.2,
    viscosity_liquid=1e-3,
    viscosity_gas=1.8e-5,
    surface_tension=0.072,
)
_VSL_VALUES = [10 ** (-3 + 3.7 * i / 39) for i in range(40)]  # 0.001 … 5
_VSG_VALUES = [10 ** (-2 + 3.7 * i / 39) for i in range(40)]  # 0.01 … 50
_STRATIFIED_PATTERNS = {_STRATIFIED, _WAVY}

_ALLOWED_REASONS = {
    FlowPatternCode.SINGLE_LIQUID: {TaitelDuklerReason.SINGLE_PHASE},
    FlowPatternCode.SINGLE_GAS: {TaitelDuklerReason.SINGLE_PHASE},
    _STRATIFIED: {
        TaitelDuklerReason.STRATIFIED_SMOOTH,
        TaitelDuklerReason.STRATIFIED_WAVY,  # при distinguish_wavy=False
    },
    _WAVY: {TaitelDuklerReason.STRATIFIED_WAVY},
    _ANNULAR: {TaitelDuklerReason.ANNULAR_LOW_LEVEL, TaitelDuklerReason.NO_EQUILIBRIUM},
    _DISPERSED: {
        TaitelDuklerReason.DISPERSED_BUBBLE,
        TaitelDuklerReason.NO_EQUILIBRIUM,
    },
    _SLUG: {TaitelDuklerReason.INTERMITTENT, TaitelDuklerReason.NO_EQUILIBRIUM},
}


def _model(
    angle: float = 0.0, settings: TaitelDuklerSettings | None = None
) -> TaitelDuklerModel:
    return TaitelDuklerModel(
        PipeParams(0.05, 1e-5, angle), _WATER_AIR, settings=settings
    )


def _grid() -> list[tuple[float, float]]:
    return [(vsl, vsg) for vsl in _VSL_VALUES for vsg in _VSG_VALUES]


def _patterns(model: TaitelDuklerModel) -> list[FlowPatternCode]:
    return [model.classify(vsl, vsg).pattern for vsl, vsg in _grid()]


def _count(patterns: list[FlowPatternCode], kinds: set[FlowPatternCode]) -> int:
    return sum(1 for pattern in patterns if pattern in kinds)


# --- Общий контракт --------------------------------------------------------


def test_name_and_angle_limit():
    model = _model()
    assert model.name() == "Taitel-Dukler"
    assert model.angle_limit() == (-10.0, 10.0)


def test_one_phase():
    model = _model()
    assert model.get_pattern_code(0.2, 0.0) == FlowPatternCode.SINGLE_LIQUID.value
    assert model.get_pattern_code(0.0, 10.0) == FlowPatternCode.SINGLE_GAS.value
    result = model.classify(0.2, 0.0)
    assert result.reason is TaitelDuklerReason.SINGLE_PHASE
    assert result.level is None


def test_get_pattern_code_returns_classify_pattern_value():
    model = _model()
    result = model.classify(0.01, 5.0)
    assert isinstance(result, TaitelDuklerResult)
    assert model.get_pattern_code(0.01, 5.0) == result.pattern.value


@pytest.mark.parametrize(
    "vsl, vsg",
    [(-1.0, 1.0), (1.0, -1.0), (float("nan"), 1.0), (1.0, float("inf"))],
)
def test_classify_invalid_input(vsl: float, vsg: float):
    with pytest.raises(ValueError):
        _model().classify(vsl, vsg)


def test_construction_without_settings_uses_defaults():
    assert _model().settings == TaitelDuklerSettings()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"annular_level_threshold": 0.0},
        {"annular_level_threshold": 1.0},
        {"sheltering_coefficient": 0.0},
    ],
)
def test_settings_validation(kwargs):
    with pytest.raises(ValueError):
        TaitelDuklerSettings(**kwargs)


def test_settings_defaults():
    settings = TaitelDuklerSettings()
    assert settings.annular_level_threshold == 0.5
    assert settings.sheltering_coefficient == 0.01
    assert settings.distinguish_wavy is True


def test_result_diagnostics_for_stratified_flow():
    result = _model().classify(0.01, 1.0)
    assert result.pattern is _STRATIFIED
    assert result.level == pytest.approx(0.262, rel=0.02)
    assert result.gas_velocity is not None
    assert result.liquid_velocity is not None
    assert result.kh_critical_gas_velocity is not None
    assert result.gas_velocity < result.kh_critical_gas_velocity


# --- Контрольные границы (вода–воздух, d = 0.05 м, θ = 0°) -------------------

_TOLERANCE = 0.10

# (что фиксировано, значение, [(переход, режим до, режим после), ...])
_TRANSITIONS = [
    ("vsl", 0.01, [(4.3, _STRATIFIED, _WAVY), (26.6, _WAVY, _ANNULAR)]),
    ("vsl", 0.1, [(2.06, _STRATIFIED, _WAVY), (10.2, _WAVY, _ANNULAR)]),
    ("vsg", 0.1, [(0.134, _STRATIFIED, _SLUG), (3.10, _SLUG, _DISPERSED)]),
    ("vsg", 1.0, [(0.161, _STRATIFIED, _SLUG), (4.92, _SLUG, _DISPERSED)]),
]


@pytest.mark.parametrize("fixed, value, transitions", _TRANSITIONS)
def test_control_transitions(fixed, value, transitions):
    model = _model()

    def pattern_at(variable: float) -> FlowPatternCode:
        vsl, vsg = (value, variable) if fixed == "vsl" else (variable, value)
        return model.classify(vsl, vsg).pattern

    for transition, before, after in transitions:
        assert pattern_at(transition * (1.0 - _TOLERANCE)) is before
        assert pattern_at(transition * (1.0 + _TOLERANCE)) is after


# --- Свойства --------------------------------------------------------------


def test_stratified_area_depends_on_inclination():
    areas = {
        angle: _count(_patterns(_model(angle)), _STRATIFIED_PATTERNS)
        for angle in (-10.0, 0.0, 10.0)
    }
    assert areas[10.0] < areas[0.0] < areas[-10.0]


@pytest.mark.parametrize("angle", [-10.0, 0.0, 10.0])
def test_reason_is_consistent_with_pattern(angle: float):
    model = _model(angle)
    for vsl, vsg in _grid():
        result = model.classify(vsl, vsg)
        assert result.reason in _ALLOWED_REASONS[result.pattern], (vsl, vsg, result)
        if result.pattern in (_ANNULAR, _DISPERSED, _SLUG):
            assert result.kh_critical_gas_velocity is not None
            assert result.gas_velocity is not None
            assert result.gas_velocity >= result.kh_critical_gas_velocity


@pytest.mark.parametrize("angle", [-10.0, 0.0, 10.0])
def test_wavy_code_is_absent_when_not_distinguished(angle: float):
    model = _model(angle, TaitelDuklerSettings(distinguish_wavy=False))
    assert _WAVY not in _patterns(model)


def test_wavy_flow_is_merged_into_stratified_when_not_distinguished():
    merged = _model(0.0, TaitelDuklerSettings(distinguish_wavy=False))
    separate = _model(0.0)
    assert separate.classify(0.01, 10.0).pattern is _WAVY
    result = merged.classify(0.01, 10.0)
    assert result.pattern is _STRATIFIED
    assert result.reason is TaitelDuklerReason.STRATIFIED_WAVY


@pytest.mark.parametrize("angle", [-10.0, 0.0, 10.0])
def test_lower_annular_threshold_does_not_increase_annular_area(angle: float):
    default = _count(_patterns(_model(angle)), {_ANNULAR})
    lowered = _count(
        _patterns(_model(angle, TaitelDuklerSettings(annular_level_threshold=0.35))),
        {_ANNULAR},
    )
    assert lowered <= default


def test_no_equilibrium_branch(monkeypatch):
    """Нет равновесного уровня: шаги 3–4 на уровне с минимальной невязкой."""
    monkeypatch.setattr(
        taitel_dukler,
        "solve_equilibrium_level",
        lambda **_: EquilibriumLevel(level=None, all_roots=()),
    )
    model = _model()
    patterns = set()
    for vsl, vsg in _grid():
        result = model.classify(vsl, vsg)
        assert result.pattern in (_ANNULAR, _DISPERSED, _SLUG)
        assert result.reason is TaitelDuklerReason.NO_EQUILIBRIUM
        assert result.level is not None
        assert result.kh_critical_gas_velocity is None
        patterns.add(result.pattern)
    assert len(patterns) > 1


# --- Производительность ----------------------------------------------------


@pytest.mark.parametrize("angle", [0.0, 10.0, -10.0])
def test_performance_10k_calls(angle: float):
    model = _model(angle)
    vsl_values = [0.01 * (500.0 ** (i / 99.0)) for i in range(100)]
    vsg_values = [0.1 * (300.0 ** (i / 99.0)) for i in range(100)]
    durations = []
    for _ in range(2):  # лучший из двух прогонов: устойчиво к фоновой нагрузке
        start = time.perf_counter()
        for vsl in vsl_values:
            for vsg in vsg_values:
                model.get_pattern_code(vsl, vsg)
        durations.append(time.perf_counter() - start)
    assert min(durations) < 3.0
