import math
from unittest.mock import Mock

import pytest

from flowmaputility.correlations.ansari import AnsariModel
from flowmaputility.correlations.ansari_vba import AnsariVBAModel
from flowmaputility.correlations.barnea import BarneaModel, BarneaSettings
from flowmaputility.correlations.beggs_brill import BeggsBrillModel
from flowmaputility.correlations.factory import ModelFactory
from flowmaputility.correlations.hasan_kabir import HasanKabirModel, HasanKabirSettings
from flowmaputility.correlations.mukherjee_brill import MukherjeeBrillModel
from flowmaputility.correlations.taitel_dukler import (
    TaitelDuklerModel,
    TaitelDuklerSettings,
)


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


def test_factory_mukherjee_brill_key(creating_Pipe):
    factory = ModelFactory()
    model = factory.creat_model("mukherjee_brill", creating_Pipe, Mock())
    assert type(model) is MukherjeeBrillModel
    assert model.name() == "Mukherjee-Brill"


@pytest.mark.parametrize("name", ["Mukherjee-Brill", "MUKHERJEE BRILL"])
def test_factory_mukherjee_brill_name_variants(name: str):
    factory = ModelFactory()
    model = factory.creat_model(name, Mock(angle=-45.0), Mock())
    assert type(model) is MukherjeeBrillModel


def test_factory_mukherjee_brill_angle_range_is_validated():
    factory = ModelFactory()
    with pytest.raises(ValueError):
        factory.creat_model("mukherjee_brill", Mock(angle=91.0), Mock())


def test_factory_auto_selection_unchanged_by_mukherjee_brill():
    factory = ModelFactory()
    assert factory.AUTO == [(0.0, 75.0, "barnea"), (75.0, 90.0, "ansari")]
    factory.MODELS["barnea"] = Mock(return_value="barnea_instance")
    expected = {
        0.0: "barnea_instance",
        45.0: "barnea_instance",
    }
    for angle, instance in expected.items():
        assert factory.creat_model(angle, Mock(angle=angle), Mock()) == instance
    for angle in (80.0, 90.0):
        model = factory.creat_model(angle, Mock(angle=angle), Mock())
        assert type(model) is AnsariModel


def test_factory_barnea_key(creating_Pipe):
    factory = ModelFactory()
    model = factory.creat_model("barnea", creating_Pipe, Mock())
    assert type(model) is BarneaModel
    assert model.name() == "Barnea"
    assert model.settings == BarneaSettings()


def test_factory_barnea_supports_negative_angles():
    factory = ModelFactory()
    model = factory.creat_model("Barnea", Mock(angle=-45.0), Mock())
    assert type(model) is BarneaModel


def test_factory_taitel_dukler_key():
    factory = ModelFactory()
    model = factory.creat_model("taitel_dukler", Mock(angle=5.0), Mock())
    assert type(model) is TaitelDuklerModel
    assert model.name() == "Taitel-Dukler"
    assert model.settings == TaitelDuklerSettings()


@pytest.mark.parametrize("name", ["Taitel-Dukler", "TAITEL DUKLER"])
def test_factory_taitel_dukler_name_variants(name: str):
    factory = ModelFactory()
    model = factory.creat_model(name, Mock(angle=0.0), Mock())
    assert type(model) is TaitelDuklerModel


def test_factory_taitel_dukler_angle_range_is_validated():
    factory = ModelFactory()
    with pytest.raises(ValueError):
        factory.creat_model("taitel_dukler", Mock(angle=45.0), Mock())


def test_factory_hasan_kabir_key(creating_Pipe):
    factory = ModelFactory()
    model = factory.creat_model("hasan_kabir", creating_Pipe, Mock())
    assert type(model) is HasanKabirModel
    assert model.name() == "Hasan-Kabir"
    assert model.settings == HasanKabirSettings()


@pytest.mark.parametrize("name", ["Hasan-Kabir", "HASAN KABIR"])
def test_factory_hasan_kabir_name_variants(name: str, creating_Pipe):
    factory = ModelFactory()
    model = factory.creat_model(name, creating_Pipe, Mock())
    assert type(model) is HasanKabirModel


def test_factory_hasan_kabir_angle_range_is_validated():
    factory = ModelFactory()
    with pytest.raises(ValueError):
        factory.creat_model("hasan_kabir", Mock(angle=30.0), Mock())
