import math
import time

import pytest

from flowmaputility.correlations.base import FlowPatternCode
from flowmaputility.correlations.mukherjee_brill import (
    STEEP_DOWNFLOW_ANGLE_DEG,
    MukherjeeBrillModel,
    MukherjeeBrillReason,
    MukherjeeBrillResult,
)
from flowmaputility.domain.params import FluidParams, PipeParams

_BUBBLE = FlowPatternCode.BUBBLE
_SLUG = FlowPatternCode.SLUG
_ANNULAR = FlowPatternCode.ANNULAR
_STRATIFIED = FlowPatternCode.STRATIFIED

_WATER_AIR = FluidParams(
    density_liquid=1000.0,
    density_gas=1.2,
    viscosity_liquid=1e-3,
    viscosity_gas=1.8e-5,
    surface_tension=0.072,
)
_ANGLES = [90.0, 45.0, 10.0, 0.0, -10.0, -20.0, -30.0, -30.001, -45.0, -80.0, -90.0]
_VSL_VALUES = [10 ** (-2 + 3.0 * i / 39) for i in range(40)]
_VSG_VALUES = [10 ** (-2 + 4.0 * i / 39) for i in range(40)]

_UPFLOW_REASONS = {
    MukherjeeBrillReason.BUBBLE_UPFLOW: _BUBBLE,
    MukherjeeBrillReason.SLUG_UPFLOW: _SLUG,
}
_STEEP_REASONS = {
    MukherjeeBrillReason.SLUG_STEEP_DOWNFLOW_LOW_GAS: _SLUG,
    MukherjeeBrillReason.SLUG_STEEP_DOWNFLOW: _SLUG,
    MukherjeeBrillReason.STRATIFIED_STEEP_DOWNFLOW: _STRATIFIED,
}
_MILD_REASONS = {
    MukherjeeBrillReason.BUBBLE_MILD_DOWNFLOW: _BUBBLE,
    MukherjeeBrillReason.SLUG_MILD_DOWNFLOW: _SLUG,
    MukherjeeBrillReason.STRATIFIED_MILD_DOWNFLOW: _STRATIFIED,
}


def _model(angle: float, fluid: FluidParams = _WATER_AIR) -> MukherjeeBrillModel:
    return MukherjeeBrillModel(PipeParams(0.05, 1e-5, angle), fluid)


def _grid() -> list[tuple[float, float]]:
    return [(vsl, vsg) for vsl in _VSL_VALUES for vsg in _VSG_VALUES]


# --- Общий контракт --------------------------------------------------------


def test_name_and_angle_limit():
    model = _model(90.0)
    assert model.name() == "Mukherjee-Brill"
    assert model.angle_limit() == (-90.0, 90.0)


def test_one_phase():
    model = _model(45.0)
    assert model.get_pattern_code(0.2, 0.0) == FlowPatternCode.SINGLE_LIQUID.value
    assert model.get_pattern_code(0.0, 10.0) == FlowPatternCode.SINGLE_GAS.value
    assert model.get_pattern_code(0.0, 0.0) == FlowPatternCode.SINGLE_GAS.value
    assert model.classify(0.2, 0.0).reason is MukherjeeBrillReason.SINGLE_PHASE


def test_get_pattern_code_returns_classify_pattern_value():
    model = _model(90.0)
    result = model.classify(0.3, 30.0)
    assert isinstance(result, MukherjeeBrillResult)
    assert model.get_pattern_code(0.3, 30.0) == result.pattern.value


@pytest.mark.parametrize(
    "vsl, vsg",
    [(-1.0, 1.0), (1.0, -1.0), (float("nan"), 1.0), (1.0, float("inf"))],
)
def test_classify_invalid_input(vsl: float, vsg: float):
    with pytest.raises(ValueError):
        _model(90.0).classify(vsl, vsg)


def test_boundaries_in_result():
    upflow = _model(90.0).classify(0.3, 1.0)
    assert upflow.stratified_boundary is None
    downflow = _model(-20.0).classify(0.3, 1.0)
    assert downflow.stratified_boundary is not None
    assert downflow.slug_annular_boundary == upflow.slug_annular_boundary


# --- Пример 4.8 ------------------------------------------------------------


def test_example_4_8():
    model = MukherjeeBrillModel(
        PipeParams(0.1524, 1.83e-5, 90.0),
        FluidParams(
            density_liquid=761.7,
            density_gas=94.1,
            viscosity_liquid=0.97e-3,
            viscosity_gas=0.016e-3,
            surface_tension=8.41e-3,
        ),
    )
    result = model.classify(1.208, 1.173)
    assert result.pattern is _SLUG
    assert result.reason is MukherjeeBrillReason.SLUG_UPFLOW
    assert result.liquid_velocity_number == pytest.approx(11.87, rel=0.01)
    assert result.gas_velocity_number == pytest.approx(11.54, rel=0.01)
    assert result.liquid_viscosity_number == pytest.approx(0.0118, rel=0.02)
    assert result.slug_annular_boundary == pytest.approx(350.8, rel=0.01)
    assert result.bubble_slug_boundary == pytest.approx(18.40, rel=0.01)
    assert result.stratified_boundary is None


# --- Контрольные переходы (вода–воздух) -------------------------------------

_TRANSITION_TOLERANCE = 0.03

# (угол, v_SL, [(v_Sg перехода, режим до, режим после), ...])
_TRANSITIONS = [
    (90.0, 0.3, [(0.204, _BUBBLE, _SLUG), (17.5, _SLUG, _ANNULAR)]),
    (90.0, 0.01, [(6.53, _SLUG, _ANNULAR)]),
    (-20.0, 0.3, [(9.10, _STRATIFIED, _SLUG), (17.5, _SLUG, _ANNULAR)]),
    (-20.0, 3.0, [(0.422, _STRATIFIED, _BUBBLE), (0.947, _BUBBLE, _SLUG)]),
    (
        -80.0,
        0.3,
        [
            (0.070, _SLUG, _STRATIFIED),
            (3.69, _STRATIFIED, _SLUG),
            (17.5, _SLUG, _ANNULAR),
        ],
    ),
    (-80.0, 3.0, [(92.3, _SLUG, _ANNULAR)]),
]


@pytest.mark.parametrize("angle, vsl, transitions", _TRANSITIONS)
def test_control_transitions(angle: float, vsl: float, transitions):
    model = _model(angle)
    for vsg, before, after in transitions:
        low = model.classify(vsl, vsg * (1.0 - _TRANSITION_TOLERANCE)).pattern
        high = model.classify(vsl, vsg * (1.0 + _TRANSITION_TOLERANCE)).pattern
        assert (low, high) == (before, after), (angle, vsl, vsg)


def test_steep_downflow_has_no_bubble_at_high_liquid_rate():
    model = _model(-80.0)
    assert all(model.classify(3.0, vsg).pattern is not _BUBBLE for vsg in _VSG_VALUES)


# --- Свойства --------------------------------------------------------------


@pytest.fixture(params=_ANGLES)
def angle_model(request) -> tuple[float, MukherjeeBrillModel]:
    return request.param, _model(request.param)


@pytest.fixture(params=[a for a in _ANGLES if a > 0.0])
def upflow_model(request) -> MukherjeeBrillModel:
    return _model(request.param)


@pytest.fixture(params=[a for a in _ANGLES if -STEEP_DOWNFLOW_ANGLE_DEG <= a <= 0.0])
def mild_model(request) -> MukherjeeBrillModel:
    return _model(request.param)


@pytest.fixture(params=[a for a in _ANGLES if a < -STEEP_DOWNFLOW_ANGLE_DEG])
def steep_model(request) -> MukherjeeBrillModel:
    return _model(request.param)


def test_annular_boundary_is_independent_of_angle_and_decides_annular(angle_model):
    angle, model = angle_model
    reference = _model(90.0)
    for vsl, vsg in _grid():
        result = model.classify(vsl, vsg)
        expected = reference.classify(vsl, vsg).slug_annular_boundary
        assert result.slug_annular_boundary == pytest.approx(expected, rel=1e-12)
        is_annular = result.gas_velocity_number > result.slug_annular_boundary
        assert (result.pattern is _ANNULAR) == is_annular


def test_upflow_never_stratified(upflow_model):
    model = upflow_model
    assert all(
        model.classify(vsl, vsg).pattern is not _STRATIFIED for vsl, vsg in _grid()
    )


def test_mild_downflow_low_liquid_rate_is_stratified(mild_model):
    model = mild_model
    checked = 0
    for vsl, vsg in _grid():
        result = model.classify(vsl, vsg)
        assert result.stratified_boundary is not None
        if result.pattern is _ANNULAR:
            continue
        if result.liquid_velocity_number <= result.stratified_boundary:
            assert result.pattern is _STRATIFIED
            checked += 1
    assert checked > 0


def test_steep_downflow_has_no_bubble(steep_model):
    model = steep_model
    assert all(model.classify(vsl, vsg).pattern is not _BUBBLE for vsl, vsg in _grid())


def test_steep_downflow_low_gas_is_slug(steep_model):
    model = steep_model
    checked = 0
    for vsl, vsg in _grid():
        result = model.classify(vsl, vsg)
        if result.pattern is _ANNULAR:
            continue
        if result.gas_velocity_number <= result.bubble_slug_boundary:
            assert result.pattern is _SLUG
            assert result.reason is MukherjeeBrillReason.SLUG_STEEP_DOWNFLOW_LOW_GAS
            checked += 1
    assert checked > 0


def test_steep_downflow_angle_boundary_is_strict():
    """θ = −30° — пологая ветвь, θ = −30.001° — крутая."""
    mild = _model(-STEEP_DOWNFLOW_ANGLE_DEG)
    steep = _model(-STEEP_DOWNFLOW_ANGLE_DEG - 0.001)
    mild_reasons = {mild.classify(v, g).reason for v, g in _grid()}
    steep_reasons = {steep.classify(v, g).reason for v, g in _grid()}
    non_common = {MukherjeeBrillReason.SINGLE_PHASE, MukherjeeBrillReason.ANNULAR}
    assert (mild_reasons - non_common) <= set(_MILD_REASONS)
    assert (steep_reasons - non_common) <= set(_STEEP_REASONS)


def test_reason_is_consistent_with_pattern(angle_model):
    angle, model = angle_model
    if angle > 0.0:
        allowed = _UPFLOW_REASONS
    elif angle < -STEEP_DOWNFLOW_ANGLE_DEG:
        allowed = _STEEP_REASONS
    else:
        allowed = _MILD_REASONS
    for vsl, vsg in _grid():
        result = model.classify(vsl, vsg)
        if result.reason is MukherjeeBrillReason.ANNULAR:
            assert result.pattern is _ANNULAR
        else:
            assert allowed[result.reason] is result.pattern, (vsl, vsg, result)


def test_slug_stratified_slug_sequence_in_steep_downflow():
    """Свойство схемы рис. 4.19, а не ошибка: SLUG → STRATIFIED → SLUG по v_Sg."""
    model = _model(-80.0)
    sequence: list[FlowPatternCode] = []
    for vsg in _VSG_VALUES:
        pattern = model.classify(0.3, vsg).pattern
        if not sequence or sequence[-1] is not pattern:
            sequence.append(pattern)
    assert sequence[:3] == [_SLUG, _STRATIFIED, _SLUG]


# --- Производительность ----------------------------------------------------


@pytest.mark.parametrize("angle", [90.0, -20.0])
def test_performance_10k_calls(angle: float):
    model = _model(angle)
    vsl_values = [0.01 * (500.0 ** (i / 99.0)) for i in range(100)]
    vsg_values = [0.1 * (300.0 ** (i / 99.0)) for i in range(100)]
    start = time.perf_counter()
    for vsl in vsl_values:
        for vsg in vsg_values:
            model.get_pattern_code(vsl, vsg)
    assert time.perf_counter() - start < 3.0


def test_sin_of_horizontal_pipe_is_treated_as_downflow_branch():
    """θ = 0 относится к ветви «горизонтальный и нисходящий» (ур. 4.131, 4.133)."""
    model = _model(0.0)
    assert math.isclose(model._invariants.sin_angle, 0.0, abs_tol=1e-15)
    assert not model._invariants.is_upflow
    assert model.classify(0.3, 1.0).stratified_boundary is not None


def test_single_phase_gives_only_single_phase_codes(angle_model):
    """Однофазные случаи: только 100 (жидкость) или 101 (газ), на любых углах."""
    _, model = angle_model
    single_liquid = FlowPatternCode.SINGLE_LIQUID.value
    single_gas = FlowPatternCode.SINGLE_GAS.value
    for velocity in (0.0, 1e-12, 5e-10):
        assert model.get_pattern_code(0.5, velocity) == single_liquid
        assert model.get_pattern_code(velocity, 5.0) == single_gas
    for vsl, vsg in _grid():
        code = model.get_pattern_code(vsl, vsg)
        assert code not in (single_liquid, single_gas)
