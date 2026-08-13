import pytest


def test_for_pipe_adapter_not_valid(pipe_adapter_not_valid):
    with pytest.raises(TypeError):
        pipe_adapter_not_valid.to_si()


def test_for_pipe_adapter_all_not_SI(pipe_adapter_all_not_SI):
    pipe = pipe_adapter_all_not_SI.to_si()
    assert pipe.diameter == 1
    assert pipe.roughness == 0.1
    assert pipe.angle == 45.0


def test_for_pipe_adapter_all_SI(pipe_adapter_all_SI):
    pipe = pipe_adapter_all_SI.to_si()
    assert pipe.diameter == 0.1
    assert pipe.roughness == 0.1
    assert pipe.angle == 45.0
