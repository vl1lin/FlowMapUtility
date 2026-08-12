from typing import TYPE_CHECKING
import pytest
from unittest.mock import Mock


if TYPE_CHECKING:
    from api.main_object import Builder
    from Run_Core.process_manager import ProcessManager
    from Correlation.fabric import ModelFabric
    from Correlation.model_abs import IFlowModel
    from Grid_Generation.grid_generator import GridGenerator
    from visualization.map import MapVisualizer
    from Grid_Generation.grid_info import GridInfo


def test_for_build_grid_info(builder: "Builder") -> None:
    builder = builder.build_grid_info()
    builder.grid_generator.assert_called_once() #type: ignore
    assert isinstance(builder, "Builder")

def test_for_decorator(builder: "Builder") -> None:
    builder.velocite_liquid = None
    builder.velocite_gas = None
    with pytest.raises(ValueError):
        builder.build_grid_info()

def test_for_build_grid_generator(builder: "Builder") -> None:
    builder.grid_generator = None
    builder = builder.build_grid_generator()
    assert isinstance(builder, "Builder")
    assert isinstance(builder.grid_generator, "GridGenerator")

def test_for_build_model_fabric(builder: "Builder") -> None:
    builder.correlation_fabric = None
    builder = builder.build_model_fabric()
    assert isinstance(builder, "Builder")
    assert isinstance(builder.correlation_fabric, "ModelFabric")

def test_for_build_model(builder: "Builder") -> None:
    builder.model = None
    builder = builder.build_model()
    assert isinstance(builder, "Builder")
    assert isinstance(builder.model, "IFlowModel")
    builder.correlation_fabric.creat_model.assert_called_once_with(builder.model_name) #type: ignore

def test_for_build_core(builder: "Builder") -> None:
    builder.run_core = None
    builder = builder.build_core()
    assert isinstance(builder, "Builder")
    assert isinstance(builder.run_core, "ProcessManager")

def test_for_build_visualization_manadger(builder: "Builder") -> None:
    builder.vis_manadger = None
    code_matrix = Mock()
    builder = builder.build_visualization_manadger(code_matrix)
    assert isinstance(builder, "Builder")
    assert isinstance(builder.vis_manadger, "MapVisualizer")

def test_for_build_all(builder: "Builder", monkeypatch: pytest.MonkeyPatch) -> None:
    builder.vis_manadger = None
    builder.correlation_fabric = None
    builder.grid_info = None
    builder.run_core = None
    builder.grid_generator = None
    builder.model = None
    monkeypatch.setattr("ProcessManager.run", Mock())
    builder = builder.build_all()
    assert isinstance(builder, "Builder")
    assert isinstance(builder.vis_manadger, "MapVisualizer")
    assert isinstance(builder.run_core, "ProcessManager")
    assert isinstance(builder.model, "IFlowModel")
    assert isinstance(builder.grid_info, "GridInfo")
    assert isinstance(builder.grid_generator, "GridGenerator")
