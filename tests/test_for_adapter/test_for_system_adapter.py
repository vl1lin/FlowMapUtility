import pytest

def test_for_system_adapter_not_valid(system_adapter_not_valid):
    with pytest.raises(TypeError):
        system_adapter_not_valid.to_si()

def test_for_system_adapter_all_not_SI(system_adapter_all_not_SI):
    system = system_adapter_all_not_SI.to_si()
    assert system.pressure == 1 * 1e6
    assert system.temperature == 273.15 + 70

def test_for_system_adapter_all_SI(system_adapter_all_SI):
    system = system_adapter_all_SI.to_si()
    assert system.pressure == 1 * 1e6
    assert system.temperature == 274
