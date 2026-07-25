from Correlation.fabric import ModelFabric
from Correlation.ansari import AnsariModel
from unittest.mock import Mock
import pytest

@pytest.mark.parametrize("name", ["Ansari", "ansari", "ANSARI"])
def test_for_fabric_name(name: str, creating_Pipe):
    fabric = ModelFabric()
    model = fabric.creat_model(name, creating_Pipe, Mock())
    assert isinstance(model, AnsariModel)
    assert model.name() == "Ansari"

@pytest.mark.parametrize("angle", [75.0, 80.0, 85.0, 90.0])
def test_fabric_for_ansari_angle(angle: float, creating_Pipe):
    fabric = ModelFabric()
    model = fabric.creat_model(angle, creating_Pipe, Mock())
    assert isinstance(model, AnsariModel)
    assert model.angle_limit() == (75.0, 90.0)
