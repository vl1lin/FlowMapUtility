from flowmaputility.correlations.base import FlowPatternCode


def test_ansari_correlation_name_angle_range(info_for_ansari_correlation):
    assert info_for_ansari_correlation.name() == "Ansari"
    min, max = 75.0, 90.0
    assert info_for_ansari_correlation.angle_limit() == (min, max)


def test_ansari_correlation_one_phase(info_for_ansari_correlation):
    assert (
        info_for_ansari_correlation.get_pattern_code(0.2, 0)
        == FlowPatternCode.SINGLE_LIQUID.value
    )
    assert (
        info_for_ansari_correlation.get_pattern_code(0, 10)
        == FlowPatternCode.SINGLE_GAS.value
    )


def test_ansari_correlation_get_pattern_code(info_for_ansari_correlation):
    assert (
        info_for_ansari_correlation.get_pattern_code(0.3, 3.0)
        == FlowPatternCode.ANNULAR.value
    )
    assert (
        info_for_ansari_correlation.get_pattern_code(0.1, 1.0)
        == FlowPatternCode.SLUG.value
    )
    assert (
        info_for_ansari_correlation.get_pattern_code(2.5, 0.1)
        == FlowPatternCode.DISPERSED_BUBBLE.value
    )
    # assert (
    #     info_for_ansari_correlation.get_pattern_code(100, 100)
    #     == FlowPatternCode.UNKNOWN.value
    # )


# def test_board_for_slug(info_for_ansari_correlation):
#     get = info_for_ansari_correlation.get_pattern_code
#     assert get(0.5, 5.0) == FlowPatternCode.SLUG.value
#     assert get(0.5, 1.7) == FlowPatternCode.SLUG.value
#     assert get(0.5, 1.72) == FlowPatternCode.SLUG.value
#     assert get(0.5, 1.73) == FlowPatternCode.DISPERSED_BUBBLE.value
