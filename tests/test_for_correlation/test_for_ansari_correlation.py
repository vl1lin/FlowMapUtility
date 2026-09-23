import json
import time
from pathlib import Path

import pytest

from flowmaputility.correlations.ansari import (
    AnsariModel,
    AnsariResult,
    AnsariSettings,
    TransitionReason,
    dispersion_prefactor,
    dispersion_terms,
    minimum_bubble_diameter,
    slip_velocity,
    turner_velocity,
)
from flowmaputility.correlations.ansari_vba import AnsariVBAModel
from flowmaputility.correlations.base import FlowPatternCode
from flowmaputility.domain.params import FluidParams, PipeParams

_REFERENCE = json.loads(
    (Path(__file__).parent / "fixtures" / "ansari_vba_reference.json").read_text(
        encoding="utf-8"
    )
)
_CASES = _REFERENCE["cases"]
_MIN_OVERALL_AGREEMENT = 0.9

_REJECTION_REASONS = {
    TransitionReason.BELOW_TURNER,
    TransitionReason.NO_FILM_SOLUTION,
    TransitionReason.BLOCKAGE,
    TransitionReason.FILM_INSTABILITY,
}


def _pipe_and_fluid(case: str) -> tuple[PipeParams, FluidParams]:
    p = _CASES[case]["params"]
    return (
        PipeParams(p["d"], p["eps"], p["angle"]),
        FluidParams(p["rl"], p["rg"], p["ml"], p["mg"], p["sig"]),
    )


def _grid() -> list[tuple[float, float]]:
    return [(vsl, vsg) for vsl in _REFERENCE["vsl"] for vsg in _REFERENCE["vsg"]]


@pytest.fixture(params=list(_CASES))
def case_models(request):
    pipe, fluid = _pipe_and_fluid(request.param)
    full = AnsariModel(pipe, fluid)
    turner_only = AnsariModel(
        pipe, fluid, settings=AnsariSettings(annular_criteria="turner_only")
    )
    return request.param, full, turner_only, AnsariVBAModel(pipe, fluid)


# --- Общий контракт --------------------------------------------------------


def test_ansari_correlation_name_angle_range(info_for_ansari_correlation):
    assert info_for_ansari_correlation.name() == "Ansari"
    assert info_for_ansari_correlation.angle_limit() == (75.0, 90.0)


def test_ansari_correlation_one_phase(info_for_ansari_correlation):
    model = info_for_ansari_correlation
    assert model.get_pattern_code(0.2, 0) == FlowPatternCode.SINGLE_LIQUID.value
    assert model.get_pattern_code(0, 10) == FlowPatternCode.SINGLE_GAS.value
    assert model.classify(0.2, 0).reason is TransitionReason.SINGLE_PHASE


def test_ansari_correlation_get_pattern_code(info_for_ansari_correlation):
    model = info_for_ansari_correlation
    assert model.get_pattern_code(0.3, 3.0) == FlowPatternCode.SLUG.value
    assert model.get_pattern_code(0.1, 1.0) == FlowPatternCode.SLUG.value
    assert model.get_pattern_code(2.5, 0.1) == FlowPatternCode.DISPERSED_BUBBLE.value
    assert model.get_pattern_code(0.3, 30.0) == FlowPatternCode.ANNULAR.value
    assert model.get_pattern_code(0.05, 0.05) == FlowPatternCode.BUBBLE.value


def test_get_pattern_code_returns_classify_pattern_value(info_for_ansari_correlation):
    model = info_for_ansari_correlation
    result = model.classify(0.3, 30.0)
    assert isinstance(result, AnsariResult)
    assert model.get_pattern_code(0.3, 30.0) == result.pattern.value


@pytest.mark.parametrize(
    "vsl, vsg",
    [(-1.0, 1.0), (1.0, -1.0), (float("nan"), 1.0), (1.0, float("inf"))],
)
def test_classify_invalid_input(info_for_ansari_correlation, vsl, vsg):
    with pytest.raises(ValueError):
        info_for_ansari_correlation.classify(vsl, vsg)


def test_construction_without_settings_uses_defaults():
    model = AnsariModel(
        PipeParams(0.1, 1e-5, 90.0), FluidParams(750, 80, 5e-4, 1e-5, 0.02)
    )
    assert model.settings == AnsariSettings()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"dispersed_max_gas_fraction": 0.0},
        {"dispersed_max_gas_fraction": 1.5},
        {"blockage_threshold": 0.0},
        {"blockage_threshold": 0.7},
        {"film_friction_ratio": 0.0},
        {"annular_criteria": "other"},
    ],
)
def test_settings_validation(kwargs):
    with pytest.raises(ValueError):
        AnsariSettings(**kwargs)


def test_settings_defaults():
    settings = AnsariSettings()
    assert settings.dispersed_max_gas_fraction == 0.76
    assert settings.blockage_threshold == 0.12
    assert settings.bubble_min_angle_deg == 70.0
    assert settings.turner_uses_inclination is True
    assert settings.film_friction_ratio == 1.0
    assert settings.annular_criteria == "full"


# --- 8.1. Пример 4.9 -------------------------------------------------------

_VSL_4_9 = 1.208
_VSG_4_9 = 1.173


@pytest.fixture
def example_4_9():
    pipe = PipeParams(diameter=0.1524, roughness=1.83e-5, angle=90.0)
    fluid = FluidParams(
        density_liquid=761.7,
        density_gas=94.1,
        viscosity_liquid=0.97e-3,
        viscosity_gas=0.016e-3,
        surface_tension=8.41e-3,
    )
    return pipe, fluid, AnsariModel(pipe, fluid)


def test_example_4_9_result(example_4_9):
    *_, model = example_4_9
    result = model.classify(_VSL_4_9, _VSG_4_9)
    assert result.pattern is FlowPatternCode.SLUG
    assert result.reason is TransitionReason.BLOCKAGE
    assert result.film is not None


def test_example_4_9_film_state(example_4_9):
    *_, model = example_4_9
    film = model.classify(_VSL_4_9, _VSG_4_9).film
    assert film is not None
    assert film.delta is not None
    assert film.film_holdup is not None
    assert film.blockage_value is not None
    assert film.entrainment_fraction == pytest.approx(0.547, rel=0.01)
    assert film.core_liquid_fraction == pytest.approx(0.36, rel=0.03)
    assert film.core_density == pytest.approx(334.4, rel=0.02)
    assert film.x_m_squared == pytest.approx(0.228, rel=0.06)
    assert film.y_m == pytest.approx(74.65, rel=0.06)
    assert film.delta == pytest.approx(0.1265, rel=0.06)
    assert film.film_holdup == pytest.approx(0.442, rel=0.06)
    assert film.blockage_value == pytest.approx(0.66, rel=0.05)
    assert film.blockage_value > model.settings.blockage_threshold


def test_example_4_9_not_dispersed(example_4_9):
    pipe, fluid, _ = example_4_9
    prefactor = dispersion_prefactor(
        liquid_density=fluid.density_liquid,
        gas_density=fluid.density_gas,
        surface_tension=fluid.surface_tension,
    )
    left, right = dispersion_terms(
        liquid_velocity=_VSL_4_9,
        gas_velocity=_VSG_4_9,
        diameter=pipe.diameter,
        relative_roughness=pipe.roughness / pipe.diameter,
        liquid_density=fluid.density_liquid,
        gas_density=fluid.density_gas,
        liquid_viscosity=fluid.viscosity_liquid,
        gas_viscosity=fluid.viscosity_gas,
        prefactor=prefactor,
    )
    assert left == pytest.approx(1.144, rel=0.05)
    assert right == pytest.approx(3.636, rel=0.05)
    assert left < right


def test_example_4_9_bubble_and_turner_quantities(example_4_9):
    _, fluid, _ = example_4_9
    kwargs = {
        "liquid_density": fluid.density_liquid,
        "gas_density": fluid.density_gas,
        "surface_tension": fluid.surface_tension,
    }
    assert turner_velocity(**kwargs) == pytest.approx(0.87, rel=0.02)
    assert slip_velocity(**kwargs) == pytest.approx(0.151, rel=0.02)
    assert minimum_bubble_diameter(**kwargs) == pytest.approx(0.0189, rel=0.02)


# --- 8.2. Согласованность с AnsariVBAModel ---------------------------------


def test_turner_only_differs_from_vba_only_in_dispersed_region(case_models):
    """
    Новая модель в режиме "turner_only" и AnsariVBAModel расходятся только там,
    где новая модель даёт DISPERSED_BUBBLE; вне этой области совпадение полное.
    Причины расхождений (известные отличия старого кода, его логика не менялась):

    * порядок проверок: старая модель проверяет Тёрнер раньше дисперсного режима
      (ANNULAR вместо DISPERSED_BUBBLE при v_Sg ≥ v_Sg,T), новая — как в примере
      4.9, дисперсный режим первым;
    * `_dbtran` при hgg = 0 возвращает граничную v_SL как скорость смеси
      (vsl = vm вместо vm − vsg), поэтому область дисперсного режима у старой
      модели меньше.
    """
    _, _, turner_only, vba = case_models
    points = _grid()
    dispersed = FlowPatternCode.DISPERSED_BUBBLE.value
    mismatches = [
        (vsl, vsg)
        for vsl, vsg in points
        if turner_only.get_pattern_code(vsl, vsg) != vba.get_pattern_code(vsl, vsg)
    ]
    assert all(turner_only.get_pattern_code(v, g) == dispersed for v, g in mismatches)
    assert 1.0 - len(mismatches) / len(points) >= _MIN_OVERALL_AGREEMENT


# --- 8.3. Свойства ---------------------------------------------------------


def test_below_turner_is_not_annular(case_models):
    _, full, _, _ = case_models
    limit = full._invariants.turner_velocity
    for vsl, vsg in _grid():
        if vsg < limit:
            assert full.classify(vsl, vsg).pattern is not FlowPatternCode.ANNULAR


def test_high_gas_fraction_is_not_dispersed(case_models):
    _, full, _, _ = case_models
    limit = full.settings.dispersed_max_gas_fraction
    for vsl, vsg in _grid():
        if vsg / (vsl + vsg) > limit:
            pattern = full.classify(vsl, vsg).pattern
            assert pattern is not FlowPatternCode.DISPERSED_BUBBLE


def test_bubble_impossible_for_small_diameter():
    """d ≤ d_min (ур. 4.158): пузырьковый режим невозможен на всей сетке."""
    fluid = FluidParams(750, 80, 5e-4, 1.5e-5, 0.02)
    d_min = minimum_bubble_diameter(
        liquid_density=fluid.density_liquid,
        gas_density=fluid.density_gas,
        surface_tension=fluid.surface_tension,
    )
    model = AnsariModel(PipeParams(0.5 * d_min, 1.5e-5, 90.0), fluid)
    assert all(
        model.classify(vsl, vsg).pattern is not FlowPatternCode.BUBBLE
        for vsl, vsg in _grid()
    )


def test_bubble_impossible_below_min_angle():
    pipe = PipeParams(0.1, 1.5e-5, 80.0)
    fluid = FluidParams(750, 80, 5e-4, 1.5e-5, 0.02)
    strict = AnsariModel(
        pipe, fluid, settings=AnsariSettings(bubble_min_angle_deg=85.0)
    )
    default = AnsariModel(pipe, fluid)
    assert default.classify(0.05, 0.05).pattern is FlowPatternCode.BUBBLE
    assert strict.classify(0.05, 0.05).pattern is FlowPatternCode.SLUG


def test_reason_is_consistent_with_pattern(case_models):
    _, full, _, _ = case_models
    allowed = {
        FlowPatternCode.SINGLE_LIQUID: {TransitionReason.SINGLE_PHASE},
        FlowPatternCode.SINGLE_GAS: {TransitionReason.SINGLE_PHASE},
        FlowPatternCode.DISPERSED_BUBBLE: {TransitionReason.DISPERSED_BUBBLE},
        FlowPatternCode.ANNULAR: {TransitionReason.ANNULAR},
        FlowPatternCode.BUBBLE: _REJECTION_REASONS,
        FlowPatternCode.SLUG: _REJECTION_REASONS,
    }
    film_reasons = (TransitionReason.BLOCKAGE, TransitionReason.FILM_INSTABILITY)
    for vsl, vsg in _grid():
        result = full.classify(vsl, vsg)
        assert result.reason in allowed[result.pattern], (vsl, vsg, result)
        if result.reason is TransitionReason.BELOW_TURNER:
            assert result.film is None
        if result.reason in film_reasons:
            assert result.film is not None and result.film.delta is not None


def test_full_annular_is_subset_of_turner_only(case_models):
    _, full, turner_only, _ = case_models
    annular = FlowPatternCode.ANNULAR.value
    for vsl, vsg in _grid():
        if full.get_pattern_code(vsl, vsg) == annular:
            assert turner_only.get_pattern_code(vsl, vsg) == annular


def _annular_threshold(model: AnsariModel, vsl: float, start: float, step: float):
    vsg = start
    while model.get_pattern_code(vsl, vsg) != FlowPatternCode.ANNULAR.value:
        vsg *= step
        assert vsg < 200.0
    return vsg


def test_annular_boundary_grows_with_vsl():
    """Порог кольцевого режима зависит от v_SL и растёт с ним (п. 7 ТЗ)."""
    pipe, fluid = _pipe_and_fluid("spec_p7_90deg")
    model = AnsariModel(pipe, fluid)
    turner = model._invariants.turner_velocity

    assert model.get_pattern_code(1.26, 5.0) != FlowPatternCode.ANNULAR.value
    thresholds = [
        _annular_threshold(model, vsl, turner, 1.02) for vsl in (0.01, 0.63, 2.51)
    ]
    assert thresholds == sorted(thresholds)
    assert _annular_threshold(model, 1.26, turner, 1.02) > 5.0


@pytest.mark.parametrize(
    "vsl, expected",
    [(0.01, 3.8), (0.16, 5.6), (0.63, 6.2), (1.26, 9.7), (2.51, 18.6)],
)
def test_annular_threshold_close_to_prototype(vsl: float, expected: float):
    pipe, fluid = _pipe_and_fluid("spec_p7_90deg")
    model = AnsariModel(pipe, fluid)
    threshold = _annular_threshold(model, vsl, 1.0, 1.005)
    assert threshold == pytest.approx(expected, rel=0.2)


def test_turner_inclination_switch():
    pipe = PipeParams(0.1, 1.5e-5, 75.0)
    fluid = FluidParams(750, 80, 5e-4, 1.5e-5, 0.02)
    with_sin = AnsariModel(pipe, fluid)
    without_sin = AnsariModel(
        pipe, fluid, settings=AnsariSettings(turner_uses_inclination=False)
    )
    ratio = (
        without_sin._invariants.turner_velocity / with_sin._invariants.turner_velocity
    )
    # v_Sg,T ∝ (sin θ)^0.25
    assert ratio == pytest.approx(0.9659258262890683**-0.25, rel=1e-9)


# --- 5.4. Производительность -----------------------------------------------


def test_performance_10k_calls():
    pipe, fluid = _pipe_and_fluid("spec_p7_90deg")
    model = AnsariModel(pipe, fluid)
    vsl_values = [0.01 * (500.0 ** (i / 99.0)) for i in range(100)]
    vsg_values = [0.1 * (300.0 ** (i / 99.0)) for i in range(100)]
    start = time.perf_counter()
    for vsl in vsl_values:
        for vsg in vsg_values:
            model.get_pattern_code(vsl, vsg)
    assert time.perf_counter() - start < 3.0
