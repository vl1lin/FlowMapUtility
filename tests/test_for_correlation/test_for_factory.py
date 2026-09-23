import math
from unittest.mock import Mock

import pytest

from flowmaputility.correlations.ansari import AnsariModel
from flowmaputility.correlations.ansari_vba import AnsariVBAModel
from flowmaputility.correlations.beggs_brill import BeggsBrillModel
from flowmaputility.correlations.factory import ModelFactory


@pytest.mark.parametrize("name", ["Ansari", "ansari", "ANSARI"])
def test_for_factory_name(name: str, creating_Pipe):
    factory = ModelFactory()
    model = factory.creat_model(name, creating_Pipe, Mock())
    assert isinstance(model, AnsariModel)
    assert model.name() == "Ansari"


@pytest.mark.parametrize(
    "name", ["Beggs-Brill", "beggs_brill", "BEGGS BRILL", "beggs-brill"]
)
def test_for_factory_name_beggs_brill(name: str, creating_Pipe_Beggs_Brill):
    factory = ModelFactory()
    model = factory.creat_model(name, creating_Pipe_Beggs_Brill, Mock())
    assert isinstance(model, BeggsBrillModel)
    assert model.name() == "Beggs-Brill"


@pytest.mark.parametrize("angle", [75.0, 80.0, 85.0, 90.0])
def test_factory_for_ansari_angle(angle: float, creating_Pipe):
    factory = ModelFactory()
    model = factory.creat_model(angle, creating_Pipe, Mock())
    assert isinstance(model, AnsariModel)
    assert model.angle_limit() == (75.0, 90.0)


@pytest.mark.parametrize("angle", [0.0, 30.0, 74.0, math.nextafter(75.0, -math.inf)])
def test_factory_for_beggs_brill_angle(angle: float):
    factory = ModelFactory()
    model = factory.creat_model(angle, Mock(), Mock())
    assert isinstance(model, BeggsBrillModel)
    assert model.angle_limit() == (0.0, math.nextafter(75.0, -math.inf))
    assert model.angle_limit()[1] != 75.0


def test_factory_ansari_key_is_new_model(creating_Pipe):
    factory = ModelFactory()
    model = factory.creat_model("ansari", creating_Pipe, Mock())
    assert type(model) is AnsariModel


@pytest.mark.parametrize("name", ["ansari_vba", "Ansari-VBA", "ANSARI VBA"])
def test_factory_ansari_vba_key(name: str, creating_Pipe):
    factory = ModelFactory()
    model = factory.creat_model(name, creating_Pipe, Mock())
    assert type(model) is AnsariVBAModel
    assert model.name() == "Ansari-VBA"


def test_factory_auto_at_90_degrees_is_new_ansari():
    factory = ModelFactory()
    model = factory.creat_model(90.0, Mock(angle=90.0), Mock())
    assert type(model) is AnsariModel


def test_factory_auto_never_selects_vba():
    factory = ModelFactory()
    assert "ansari_vba" not in [key for _, _, key in factory.AUTO]
    for angle in (75.0, 80.0, 90.0):
        model = factory.creat_model(angle, Mock(angle=angle), Mock())
        assert type(model) is AnsariModel


def test_factory_auto_ranges_must_not_overlap():
    factory = ModelFactory()
    factory.AUTO = [(0.0, 80.0, "beggs_brill"), (75.0, 90.0, "ansari")]
    with pytest.raises(ValueError):
        factory._validate_auto()
