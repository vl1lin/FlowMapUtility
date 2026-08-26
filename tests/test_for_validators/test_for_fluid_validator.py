import pytest

from flowmaputility.domain.validators import FluidParamsValidator


@pytest.mark.parametrize(
    [
        "density_liquid",
        "density_gas",
        "viscosity_liquid",
        "viscosity_gas",
        "surface_tension",
    ],
    [
        ("100", "109", "130", "160", "160"),
        (True, False, True, False, True),
    ],
)
def test_for_fluid_validator(
    density_liquid: float,
    density_gas: float,
    viscosity_liquid: float,
    viscosity_gas: float,
    surface_tension: float,
):
    with pytest.raises(ValueError):
        validator = FluidParamsValidator(  # noqa F841
            density_liquid,
            density_gas,
            viscosity_liquid,
            viscosity_gas,
            surface_tension,
        )


@pytest.mark.parametrize(
    [
        "density_liquid",
        "density_gas",
        "viscosity_liquid",
        "viscosity_gas",
        "surface_tension",
    ],
    [
        tuple(i for i in range(0, 5)),
        tuple(i * 1.0 for i in range(0, 5)),
    ],
)
def test_for_fluid_validator_good(
    density_liquid: float,
    density_gas: float,
    viscosity_liquid: float,
    viscosity_gas: float,
    surface_tension: float,
):
    validator = FluidParamsValidator(
        density_liquid, density_gas, viscosity_liquid, viscosity_gas, surface_tension
    )
    param = validator.validate()
    for value in vars(param).values():
        assert isinstance(value, float)
