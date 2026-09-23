import time

import pytest

from flowmaputility.correlations.barnea import (
    BarneaModel,
    BarneaReason,
    BarneaResult,
    BarneaSettings,
)
from flowmaputility.correlations.base import FlowPatternCode
from flowmaputility.domain.params import FluidParams, PipeParams

_STRATIFIED = FlowPatternCode.STRATIFIED
_WAVY = FlowPatternCode.STRATIFIED_WAVY
_BUBBLE = FlowPatternCode.BUBBLE
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
_ANGLES = [90.0, 60.0, 10.0, 0.0, -10.0, -45.0, -80.0, -90.0]
_VSL_VALUES = [10 ** (-3 + 3.7 * i / 39) for i in range(40)]  # 0.001 … 5
_VSG_VALUES = [10 ** (-2 + 3.7 * i / 39) for i in range(40)]  # 0.01 … 50

_STRATIFIED_PATTERNS = {_STRATIFIED, _WAVY}
_REJECTION_REASONS = {
    BarneaReason.NO_FILM_SOLUTION,
    BarneaReason.BLOCKAGE,
    BarneaReason.FILM_INSTABILITY,
}
_ALLOWED_REASONS = {
    FlowPatternCode.SINGLE_LIQUID: {BarneaReason.SINGLE_PHASE},
    FlowPatternCode.SINGLE_GAS: {BarneaReason.SINGLE_PHASE},
    _STRATIFIED: {BarneaReason.STRATIFIED_SMOOTH},
    _WAVY: {BarneaReason.STRATIFIED_WAVY},
    _DISPERSED: {BarneaReason.DISPERSED_BUBBLE},
    _ANNULAR: {BarneaReason.ANNULAR, BarneaReason.DOWNFLOW_ANNULAR},
    _BUBBLE: _REJECTION_REASONS,
    _SLUG: _REJECTION_REASONS,
}


def _model(
    angle: float,
    diameter: float = 0.05,
    settings: BarneaSettings | None = None,
) -> BarneaModel:
    return BarneaModel(PipeParams(diameter, 1e-5, angle), _WATER_AIR, settings=settings)


def _grid() -> list[tuple[float, float]]:
    return [(vsl, vsg) for vsl in _VSL_VALUES for vsg in _VSG_VALUES]


def _patterns(model: BarneaModel) -> list[FlowPatternCode]:
    return [model.classify(vsl, vsg).pattern for vsl, vsg in _grid()]


# --- Общий контракт --------------------------------------------------------


def test_name_and_angle_limit():
    model = _model(0.0)
    assert model.name() == "Barnea"
    assert model.angle_limit() == (-90.0, 90.0)


def test_one_phase():
    model = _model(30.0)
    assert model.get_pattern_code(0.2, 0.0) == FlowPatternCode.SINGLE_LIQUID.value
    assert model.get_pattern_code(0.0, 10.0) == FlowPatternCode.SINGLE_GAS.value
    assert model.classify(0.2, 0.0).reason is BarneaReason.SINGLE_PHASE


def test_get_pattern_code_returns_classify_pattern_value():
    model = _model(0.0)
    result = model.classify(0.01, 5.0)
    assert isinstance(result, BarneaResult)
    assert model.get_pattern_code(0.01, 5.0) == result.pattern.value


@pytest.mark.parametrize(
    "vsl, vsg",
    [(-1.0, 1.0), (1.0, -1.0), (float("nan"), 1.0), (1.0, float("inf"))],
)
def test_classify_invalid_input(vsl: float, vsg: float):
    with pytest.raises(ValueError):
        _model(0.0).classify(vsl, vsg)


def test_construction_without_settings_uses_defaults():
    assert _model(0.0).settings == BarneaSettings()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"sheltering_coefficient": 0.0},
        {"downflow_wave_froude": 0.0},
        {"dispersed_max_gas_fraction": 0.0},
        {"dispersed_max_gas_fraction": 1.5},
        {"blockage_factor": 0.0},
        {"blockage_factor": 0.7},
        {"blockage_mode": "other"},
        {"constant_slug_holdup": 0.0},
    ],
)
def test_settings_validation(kwargs):
    with pytest.raises(ValueError):
        BarneaSettings(**kwargs)


def test_settings_defaults():
    settings = BarneaSettings()
    assert settings.sheltering_coefficient == 0.01
    assert settings.downflow_wave_froude == 1.5
    assert settings.dispersed_max_gas_fraction == 0.52
    assert settings.blockage_factor == 0.5
    assert settings.blockage_mode == "barnea_brauner"
    assert settings.constant_slug_holdup == 0.48
    assert settings.bubble_min_angle_deg == 60.0


# --- Контрольные переходы (вода–воздух, d = 0.05 м) -------------------------

_TOLERANCE = 0.15

# (угол, что фиксировано, значение, [(переход, режим до, режим после), ...])
_TRANSITIONS = [
    (0.0, "vsl", 0.01, [(4.3, _STRATIFIED, _WAVY), (27.4, _WAVY, _ANNULAR)]),
    (0.0, "vsg", 0.1, [(0.135, _STRATIFIED, _SLUG), (3.61, _SLUG, _DISPERSED)]),
    (10.0, "vsl", 0.01, [(9.4, _SLUG, _ANNULAR)]),
    (90.0, "vsl", 0.01, [(23.8, _SLUG, _ANNULAR)]),
    (90.0, "vsg", 0.1, [(2.38, _SLUG, _DISPERSED)]),
    (-10.0, "vsl", 1.0, [(5.9, _WAVY, _SLUG), (18.9, _SLUG, _ANNULAR)]),
    (-80.0, "vsg", 0.1, [(0.28, _WAVY, _ANNULAR), (8.3, _ANNULAR, _DISPERSED)]),
]


@pytest.mark.parametrize("angle, fixed, value, transitions", _TRANSITIONS)
def test_control_transitions(angle, fixed, value, transitions):
    model = _model(angle)

    def pattern_at(variable: float) -> FlowPatternCode:
        vsl, vsg = (value, variable) if fixed == "vsl" else (variable, value)
        return model.classify(vsl, vsg).pattern

    for transition, before, after in transitions:
        assert pattern_at(transition * (1.0 - _TOLERANCE)) is before
        assert pattern_at(transition * (1.0 + _TOLERANCE)) is after


def test_no_bubble_flow_for_small_diameter():
    """d = 0.05 м < d_min ≈ 0.051 м: пузырькового режима нет ни при каких углах."""
    for angle in (90.0, 80.0, 60.0):
        assert _BUBBLE not in _patterns(_model(angle))


def test_bubble_flow_depends_on_angle():
    assert _model(90.0, diameter=0.1).classify(0.3, 0.02).pattern is _BUBBLE
    assert _model(45.0, diameter=0.1).classify(0.3, 0.02).pattern is not _BUBBLE


def test_downflow_annular_reason():
    result = _model(-80.0).classify(1.0, 0.1)
    assert result.pattern is _ANNULAR
    assert result.reason is BarneaReason.DOWNFLOW_ANNULAR
    assert result.level is not None


# --- Свойства --------------------------------------------------------------


@pytest.fixture(params=_ANGLES)
def angle_model(request) -> tuple[float, BarneaModel]:
    return request.param, _model(request.param)


@pytest.mark.parametrize("angle", [90.0, -90.0])
def test_no_stratified_in_vertical_pipe(angle: float):
    assert not _STRATIFIED_PATTERNS & set(_patterns(_model(angle)))


def test_stratified_area_decreases_with_upward_inclination():
    areas = {
        angle: sum(1 for p in _patterns(_model(angle)) if p in _STRATIFIED_PATTERNS)
        for angle in (-10.0, 0.0, 10.0)
    }
    assert areas[-10.0] > areas[0.0] > areas[10.0]


def test_high_gas_fraction_is_not_dispersed(angle_model):
    _, model = angle_model
    limit = model.settings.dispersed_max_gas_fraction
    for vsl, vsg in _grid():
        if vsg / (vsl + vsg) > limit:
            assert model.classify(vsl, vsg).pattern is not _DISPERSED


def test_reason_is_consistent_with_pattern(angle_model):
    _, model = angle_model
    for vsl, vsg in _grid():
        result = model.classify(vsl, vsg)
        assert result.reason in _ALLOWED_REASONS[result.pattern], (vsl, vsg, result)


def test_diagnostics_are_filled_when_computed(angle_model):
    angle, model = angle_model
    for vsl, vsg in _grid():
        result = model.classify(vsl, vsg)
        if result.reason in _REJECTION_REASONS - {BarneaReason.NO_FILM_SOLUTION}:
            assert result.film_holdup is not None
            assert result.slug_holdup is not None
        if result.reason is BarneaReason.NO_FILM_SOLUTION:
            assert result.film_holdup is None
        if result.reason is BarneaReason.ANNULAR:
            assert result.film_holdup is not None
        if result.reason in (
            BarneaReason.STRATIFIED_SMOOTH,
            BarneaReason.STRATIFIED_WAVY,
        ):
            assert result.level is not None
            assert abs(angle) < 90.0


# --- Настройки -------------------------------------------------------------


def test_constant_blockage_mode_uses_constant_slug_holdup():
    model = _model(90.0, settings=BarneaSettings(blockage_mode="constant"))
    result = model.classify(0.5, 10.0)
    assert result.slug_holdup == 0.48


def test_default_blockage_mode_computes_slug_holdup():
    result = _model(90.0).classify(0.5, 10.0)
    assert result.slug_holdup is not None
    assert 0.48 <= result.slug_holdup <= 1.0


def test_small_sheltering_coefficient_delays_waves():
    """u_G,wavy ∝ s^−0.5: малый s отодвигает волновое течение, режим становится гладким."""
    default = _model(0.0).classify(0.01, 6.0)
    smooth = _model(0.0, settings=BarneaSettings(sheltering_coefficient=1e-6)).classify(
        0.01, 6.0
    )
    assert default.pattern is _WAVY
    assert smooth.pattern is _STRATIFIED


# --- Производительность ----------------------------------------------------


@pytest.mark.parametrize("angle", [90.0, 0.0, -20.0])
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
