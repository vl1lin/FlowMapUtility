from unittest.mock import Mock

import pytest

from api.main_object import Builder
from Correlation.fabric import ModelFabric
from Grid_Generation.grid_generator import GridGenerator
from Run_Core.process_manager import ProcessManager
from visualization.map import MapVisualizer


def test_for_build_grid_info(builder: "Builder") -> None:
    builder = builder.build_grid_info()
    builder.grid_generator.generate.assert_called_once()  # type: ignore
    assert isinstance(builder, Builder)


def test_for_decorator(builder: "Builder") -> None:
    builder.velocite_liquid = None
    builder.velocite_gas = None
    with pytest.raises(ValueError):
        builder.build_grid_generator()


def test_for_build_grid_generator(builder: "Builder") -> None:
    builder.grid_generator = None
    builder = builder.build_grid_generator()
    assert isinstance(builder, Builder)
    assert isinstance(builder.grid_generator, GridGenerator)


def test_for_build_model_fabric(builder: "Builder") -> None:
    builder.correlation_fabric = None
    builder = builder.build_model_fabric()
    assert isinstance(builder, Builder)
    assert isinstance(builder.correlation_fabric, ModelFabric)


def test_for_build_model(builder: "Builder") -> None:
    builder = builder.build_model()
    assert isinstance(builder, Builder)
    builder.correlation_fabric.creat_model.assert_called_once_with(builder.model_name)  # type: ignore


def test_for_build_core(builder: "Builder") -> None:
    builder.run_core = None
    builder = builder.build_core()
    assert isinstance(builder, Builder)
    assert isinstance(builder.run_core, ProcessManager)


def test_for_build_visualization_manadger(builder: "Builder") -> None:
    builder.vis_manadger = None
    code_matrix = Mock()
    builder = builder.build_visualization_manadger(code_matrix)
    assert isinstance(builder, Builder)
    assert isinstance(builder.vis_manadger, MapVisualizer)


def test_for_build_all(builder: "Builder", monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(builder, "build_core", Mock(return_value=builder))
    monkeypatch.setattr(
        builder, "build_visualization_manadger", Mock(return_value=builder)
    )
    monkeypatch.setattr(builder, "build_model", Mock(return_value=builder))
    monkeypatch.setattr(builder, "build_model_fabric", Mock(return_value=builder))
    monkeypatch.setattr(builder, "build_grid_info", Mock(return_value=builder))
    monkeypatch.setattr(builder, "build_grid_generator", Mock(return_value=builder))
    builder = builder.build_all()
    assert isinstance(builder, Builder)
    builder.build_core.assert_called_once()  # type: ignore
    builder.build_visualization_manadger.assert_called_once()  # type: ignore
    builder.build_model.assert_called_once()  # type: ignore
    builder.build_model_fabric.assert_called_once()  # type: ignore
    builder.build_grid_info.assert_called_once()  # type: ignore
    builder.build_grid_generator.assert_called_once()  # type: ignore
