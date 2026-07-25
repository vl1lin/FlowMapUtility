import pytest
from Correlation.ansari import AnsariModel
from Data_Block_1.adapter_for_data import PipeParamsAdapter, FluidParamsAdapter
from unittest.mock import Mock

@pytest.fixture
def info_for_ansari_correlation():
    pipe = PipeParamsAdapter(0.062, 0.00005, 90).to_si()
    fluid = FluidParamsAdapter(
        800,
        50,
        0.001,
        0.00001,
        0.01
    ).to_si()
    ansari_model = AnsariModel(pipe, fluid)
    return ansari_model

@pytest.fixture
def creating_Pipe():
    pipe = Mock(angle = 80.0)
    return pipe
