import pytest

from flowmaputility.domain.validators import PipeParamsValidator


@pytest.mark.parametrize(
    ["diameter", "roughness", "angle"],
    [
        ("100", "109", "130"),
        (True, False, True),
        (1, 2.0, "3"),
    ],
)
def test_for_pipe_validator(
    diameter: float,
    roughness: float,
    angle: float,
):
    with pytest.raises(ValueError):
        validator = PipeParamsValidator(diameter, roughness, angle)  # noqa F841


@pytest.mark.parametrize(
    ["diameter", "roughness", "angle"],
    [
        tuple(i for i in range(0, 3)),
        tuple(i * 1.0 for i in range(1, 4)),
    ],
)
def test_for_pipe_validator_good(
    diameter: float,
    roughness: float,
    angle: float,
):
    validator = PipeParamsValidator(diameter, roughness, angle)

    params = validator.validate()
    for value in vars(params).values():
        assert isinstance(value, float)
