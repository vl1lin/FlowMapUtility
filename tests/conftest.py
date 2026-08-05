import pytest
import numpy as np
from Grid_Generation.grid_info import GridInfo
from Run_Core.process_manager import ProcessManager
from Data_Block_1.adapter_for_data import PipeParamsAdapter, FluidParamsAdapter, SystemParamsAdapter
from Correlation.ansari import AnsariModel
from Grid_Generation.grid_generator import GridGenerator
from unittest.mock import Mock, patch, MagicMock
from visualization.tuners import ColorTuner, GraphTuner
import math

@pytest.fixture
def pipe_adapter_not_valid():
    pipe_adapter = PipeParamsAdapter("wrong", "wrong", "wrong") #type: ignore
    return pipe_adapter

@pytest.fixture
def pipe_adapter_all_not_SI():
    pipe_adapter = PipeParamsAdapter(1000, 0.1, 45 * math.pi / 180)
    return pipe_adapter

@pytest.fixture
def pipe_adapter_all_SI():
    pipe_adapter = PipeParamsAdapter(0.1, 0.1, 45)
    return pipe_adapter

@pytest.fixture
def system_adapter_not_valid():
    system_adapter = SystemParamsAdapter("", "") #type: ignore
    return system_adapter

@pytest.fixture
def system_adapter_all_not_SI():
    system_adapter = SystemParamsAdapter(1, 70)
    return system_adapter

@pytest.fixture
def system_adapter_all_SI():
    system_adapter = SystemParamsAdapter(1 * 1e6, 274)
    return system_adapter


@pytest.fixture
def fluid_adapter_not_valid():
    fluid_adapter = FluidParamsAdapter("", "", "", "", "") #type: ignore
    return fluid_adapter

@pytest.fixture
def fluid_adapter_all_SI():
    fluid_adapter = FluidParamsAdapter(1000, 7, 0.1, 0.5, 40)
    return fluid_adapter

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

@pytest.fixture
def create_grid_generator() -> GridGenerator:
    grid = GridGenerator(
        vsl_range=(0.1, 0.5),
        vsg_range=(10.0, 15.0),
        resolution=10,
        log_scale=True,
    )
    return grid

@pytest.fixture
def create_small_grid_generator() -> GridGenerator:
    grid = GridGenerator(
        vsl_range=Mock(),
        vsg_range=Mock(),
        resolution=3,
        log_scale=Mock(),
    )
    return grid

@pytest.fixture
def create_lin_grid_generator() -> GridGenerator:
    grid = GridGenerator(
        vsl_range=(0.1, 0.5),
        vsg_range=(10.0, 15.0),
        resolution=10,
        log_scale=False,
    )
    return grid

@pytest.fixture
def create_emergency_grid_generator() -> GridGenerator:
    grid = GridGenerator(
        vsl_range=(-0.1, 0.5),
        vsg_range=(-1.0, 5.0),
        resolution=10,
        log_scale=True,
    )
    return grid

@pytest.fixture
def core_beginer(info_for_ansari_correlation):
    vsl_1d = np.array([0.1, 0.2, 0.3])
    vsl_2d = np.ones((3, 1)) * vsl_1d
    vsg_1d = np.flip(np.array([1.0, 2.0, 3.0]))
    vsg_2d = vsg_1d[:, np.newaxis] * np.ones((3,3))
    grid_info = GridInfo(vsl_1d, vsg_1d, vsl_2d, vsg_2d, 3, True)
    return ProcessManager(info_for_ansari_correlation, grid_info)

@pytest.fixture
def mock_plt():
    with patch("visualization.tuners.plt") as mock:
        yield mock

@pytest.fixture
def mock_mcolors():
    with patch("visualization.tuners.mcolors") as mock:
        yield mock

@pytest.fixture
def mock_color_tuner():
    mock_ax = MagicMock()
    mock_grid = MagicMock()
    mock_codes = MagicMock()
    tuner = ColorTuner(mock_ax, mock_grid, mock_codes)
    return tuner

@pytest.fixture
def mock_graph_tuner() -> GraphTuner:
    tuner = GraphTuner()
    return tuner
