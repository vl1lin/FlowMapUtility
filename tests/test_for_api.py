from unittest.mock import Mock

import pytest

from flowmaputility.builder import Builder
from flowmaputility.correlations.base import IFlowModel
from flowmaputility.correlations.factory import ModelFactory
from flowmaputility.domain.params import PipeParams
from flowmaputility.engine.manager import ProcessManager
from flowmaputility.grid.generator import GridGenerator
from flowmaputility.visualization.visualizer import MapVisualizer


def test_for_build_grid_info(builder: "Builder") -> None:
    builder = builder.build_grid_info()
    builder.grid_generator.generate.assert_called_once()  # type: ignore
    assert isinstance(builder, Builder)


def test_for_set_show_progress_default() -> None:
    assert Builder().show_progress is False


def test_for_set_show_progress() -> None:
    builder = Builder().set_show_progress()
    assert builder.show_progress is True

    builder = Builder().set_show_progress(False)
    assert builder.show_progress is False


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


def test_for_build_model_factory(builder: "Builder") -> None:
    builder.correlation_factory = None
    builder = builder.build_model_factory()
    assert isinstance(builder, Builder)
    assert isinstance(builder.correlation_factory, ModelFactory)


def test_for_build_model(builder: "Builder") -> None:
    builder = builder.build_model()
    assert isinstance(builder, Builder)
    builder.correlation_factory.creat_model.assert_called_once_with(  # type: ignore
        builder.model_name,
        builder.pipe_params,
        builder.fluid_params,
    )


def test_for_build_model_with_angle(builder: "Builder") -> None:
    builder.model_name = None
    builder = builder.build_model()
    assert isinstance(builder, Builder)
    builder.correlation_factory.creat_model.assert_called_once_with(  # type: ignore
        builder.pipe_params.angle,  # type: ignore
        builder.pipe_params,  # type: ignore
        builder.fluid_params,  # type: ignore
    )


def test_for_integration_build_model_with_angle(builder: "Builder") -> None:
    builder.model_name = None
    builder.pipe_params = PipeParams(diameter=1.0, roughness=0.01, angle=90.0)
    builder.correlation_factory = ModelFactory()
    builder = builder.build_model()
    assert isinstance(builder, Builder)
    assert isinstance(builder.model, IFlowModel)
    assert builder.model.name() == "Ansari"  # type: ignore


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
    monkeypatch.setattr(builder, "build_model_factory", Mock(return_value=builder))
    monkeypatch.setattr(builder, "build_grid_info", Mock(return_value=builder))
    monkeypatch.setattr(builder, "build_grid_generator", Mock(return_value=builder))
    builder = builder.build_all()
    assert isinstance(builder, Builder)
    builder.build_core.assert_called_once()  # type: ignore
    builder.build_visualization_manadger.assert_called_once()  # type: ignore
    builder.build_model.assert_called_once()  # type: ignore
    builder.build_model_factory.assert_called_once()  # type: ignore
    builder.build_grid_info.assert_called_once()  # type: ignore
    builder.build_grid_generator.assert_called_once()  # type: ignore
