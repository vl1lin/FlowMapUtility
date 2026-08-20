from unittest.mock import Mock

import pytest

from flowmaputility.correlations.ansari import AnsariModel
from flowmaputility.correlations.factory import ModelFactory


@pytest.mark.parametrize("name", ["Ansari", "ansari", "ANSARI"])
def test_for_factory_name(name: str, creating_Pipe):
    factory = ModelFactory()
    model = factory.creat_model(name, creating_Pipe, Mock())
    assert isinstance(model, AnsariModel)
    assert model.name() == "Ansari"


@pytest.mark.parametrize("angle", [75.0, 80.0, 85.0, 90.0])
def test_factory_for_ansari_angle(angle: float, creating_Pipe):
    factory = ModelFactory()
    model = factory.creat_model(angle, creating_Pipe, Mock())
    assert isinstance(model, AnsariModel)
    assert model.angle_limit() == (75.0, 90.0)
