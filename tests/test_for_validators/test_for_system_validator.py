import pytest

from flowmaputility.domain.validators import SystemParamsValidator


@pytest.mark.parametrize(["pressure", "temperature"], [("10", "20"), (True, False)])
def test_for_system_validator(pressure, temperature):
    with pytest.raises(ValueError):
        validator = SystemParamsValidator(pressure, temperature)  # noqa F841


@pytest.mark.parametrize(
    ["pressure", "temperature"],
    [tuple(i for i in range(0, 2)), tuple(i * 1.0 for i in range(0, 2))],
)
def test_for_system_validator_good(pressure, temperature):
    validator = SystemParamsValidator(pressure, temperature)
    param = validator.validate()
    for value in vars(param).values():
        assert isinstance(value, float)
