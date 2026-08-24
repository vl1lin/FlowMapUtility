import math

import pytest

from flowmaputility.correlations.base import FlowPatternCode
from flowmaputility.correlations.beggs_brill import (
    _FP_DIST,
    _FP_INT,
    _FP_SEG,
    _FP_TRANS,
    BeggsBrillModel,
)


def test_name_and_angle_limit(bb_model: BeggsBrillModel) -> None:
    assert bb_model.name() == "Beggs-Brill"
    assert bb_model.angle_limit() == (0.0, math.nextafter(75.0, 0.0))


def test_single_phase_gas(bb_model: BeggsBrillModel) -> None:
    assert bb_model.get_pattern_code(0.0, 5.0) == FlowPatternCode.SINGLE_GAS.value


def test_single_phase_liquid(bb_model: BeggsBrillModel) -> None:
    assert bb_model.get_pattern_code(0.2, 0.0) == FlowPatternCode.SINGLE_LIQUID.value


@pytest.mark.parametrize(
    "vsl, vsg, expected",
    [
        # Расслоенный (Segregated) -> STRATIFIED
        (0.01, 0.02, FlowPatternCode.STRATIFIED.value),
        (
            0.05,
            1.0,
            FlowPatternCode.STRATIFIED.value,
        ),  # lam_l мал, несмотря на большой n_fr
        # Переходная зона (Transition) -> SLUG (жёсткий маппинг по договорённости)
        (0.05, 0.05, FlowPatternCode.SLUG.value),
        (0.1, 0.05, FlowPatternCode.SLUG.value),
        # Перемежающийся (Intermittent) -> SLUG
        (0.3, 0.3, FlowPatternCode.SLUG.value),
        (0.5, 0.1, FlowPatternCode.SLUG.value),
        (3.0, 3.0, FlowPatternCode.SLUG.value),
        # Распределённый (Distributed) -> DISPERSED_BUBBLE
        (1.0, 0.05, FlowPatternCode.DISPERSED_BUBBLE.value),
    ],
)
def test_get_pattern_code_matches_rigid_map(
    bb_model: BeggsBrillModel, vsl: float, vsg: float, expected: int
) -> None:
    assert bb_model.get_pattern_code(vsl, vsg) == expected


# Отдельные юнит-тесты самой карты режимов _flow_pattern (без обвязки
# по vsl/vsg) — проверяют именно границы формул на "круглых" числах.
@pytest.mark.parametrize(
    "lam_l, n_fr, expected_fp",
    [
        (0.5, 0.001, _FP_SEG),
        (0.5, 0.05, _FP_TRANS),
        (0.5, 1.0, _FP_INT),
        (0.5, 60.0, _FP_DIST),
    ],
)
def test_flow_pattern_boundaries(
    bb_model: BeggsBrillModel, lam_l: float, n_fr: float, expected_fp: int
) -> None:
    assert bb_model._flow_pattern(lam_l, n_fr) == expected_fp
