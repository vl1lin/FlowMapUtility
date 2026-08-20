import pytest

from flowmaputility.domain.adapters import FluidParamsAdapter


def test_for_fluid_adapter_not_valid(fluid_adapter_not_valid):
    with pytest.raises(TypeError):
        fluid_adapter_not_valid.to_si()


def test_for_fluid_adapter_all_SI(fluid_adapter_all_SI):
    fluid = fluid_adapter_all_SI.to_si()
    assert fluid.density_liquid == 1000
    assert fluid.density_gas == 7
    assert fluid.viscosity_liquid == 0.1
    assert fluid.viscosity_gas == 0.5
    assert fluid.surface_tension == 0.01


def test_for_fluid_adapter_all_not_SI():
    fluid = FluidParamsAdapter(1, 0.007, 1, 5, 100)
    fluid = fluid.to_si()
    assert fluid.density_liquid == 1000
    assert fluid.density_gas == 7
    assert fluid.viscosity_liquid == 0.001
    assert fluid.viscosity_gas == 0.005
    assert fluid.surface_tension == 0.1
