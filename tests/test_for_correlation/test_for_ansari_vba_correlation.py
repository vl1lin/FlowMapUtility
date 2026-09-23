import json
from pathlib import Path

import pytest

from flowmaputility.correlations.ansari_vba import AnsariVBAModel
from flowmaputility.correlations.base import FlowPatternCode
from flowmaputility.domain.params import FluidParams, PipeParams

_REFERENCE = json.loads(
    (Path(__file__).parent / "fixtures" / "ansari_vba_reference.json").read_text(
        encoding="utf-8"
    )
)


def test_ansari_correlation_name_angle_range(info_for_ansari_vba_correlation):
    assert info_for_ansari_vba_correlation.name() == "Ansari-VBA"
    min, max = 75.0, 90.0
    assert info_for_ansari_vba_correlation.angle_limit() == (min, max)


def test_ansari_correlation_one_phase(info_for_ansari_vba_correlation):
    assert (
        info_for_ansari_vba_correlation.get_pattern_code(0.2, 0)
        == FlowPatternCode.SINGLE_LIQUID.value
    )
    assert (
        info_for_ansari_vba_correlation.get_pattern_code(0, 10)
        == FlowPatternCode.SINGLE_GAS.value
    )


def test_ansari_correlation_get_pattern_code(info_for_ansari_vba_correlation):
    assert (
        info_for_ansari_vba_correlation.get_pattern_code(0.3, 3.0)
        == FlowPatternCode.ANNULAR.value
    )
    assert (
        info_for_ansari_vba_correlation.get_pattern_code(0.1, 1.0)
        == FlowPatternCode.SLUG.value
    )
    assert (
        info_for_ansari_vba_correlation.get_pattern_code(2.5, 0.1)
        == FlowPatternCode.DISPERSED_BUBBLE.value
    )
    # assert (
    #     info_for_ansari_vba_correlation.get_pattern_code(100, 100)
    #     == FlowPatternCode.UNKNOWN.value
    # )


# def test_board_for_slug(info_for_ansari_vba_correlation):
#     get = info_for_ansari_vba_correlation.get_pattern_code
#     assert get(0.5, 5.0) == FlowPatternCode.SLUG.value
#     assert get(0.5, 1.7) == FlowPatternCode.SLUG.value
#     assert get(0.5, 1.72) == FlowPatternCode.SLUG.value
#     assert get(0.5, 1.73) == FlowPatternCode.DISPERSED_BUBBLE.value


@pytest.mark.parametrize("case", _REFERENCE["cases"])
def test_ansari_vba_matches_reference_grid(case: str):
    """Побитовое совпадение со старым AnsariModel на сетке 30×30 (фикстура)."""
    params = _REFERENCE["cases"][case]["params"]
    model = AnsariVBAModel(
        PipeParams(params["d"], params["eps"], params["angle"]),
        FluidParams(
            params["rl"], params["rg"], params["ml"], params["mg"], params["sig"]
        ),
    )
    expected = _REFERENCE["cases"][case]["codes"]
    actual = [
        [model.get_pattern_code(vsl, vsg) for vsg in _REFERENCE["vsg"]]
        for vsl in _REFERENCE["vsl"]
    ]
    assert actual == expected
