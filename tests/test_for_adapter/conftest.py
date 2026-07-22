from pytest import fixture
from Data_Block_1.adapter_for_data import PipeParamsAdapter, SystemParamsAdapter, FluidParamsAdapter

@fixture
def pipe_adapter_not_valid():
    pipe_adapter = PipeParamsAdapter("wrong", "wrong", "wrong") #type: ignore
    return pipe_adapter

@fixture
def pipe_adapter_all_not_SI():
    pipe_adapter = PipeParamsAdapter(1000, 0.1, 45)
    return pipe_adapter

@fixture
def pipe_adapter_all_SI():
    pipe_adapter = PipeParamsAdapter(0.1, 0.1, 0.6)
    return pipe_adapter

@fixture
def system_adapter_not_valid():
    system_adapter = SystemParamsAdapter("", "") #type: ignore
    return system_adapter

@fixture
def system_adapter_all_not_SI():
    system_adapter = SystemParamsAdapter(1, 70)
    return system_adapter

@fixture
def system_adapter_all_SI():
    system_adapter = SystemParamsAdapter(1 * 10e6, 274)
    return system_adapter


@fixture
def fluid_adapter_not_valid():
    fluid_adapter = FluidParamsAdapter("", "", "", "", "") #type: ignore
    return fluid_adapter

@fixture
def fluid_adapter_all_SI():
    fluid_adapter = FluidParamsAdapter(1000, 7, 0.1, 0.5, 400)
    return fluid_adapter
