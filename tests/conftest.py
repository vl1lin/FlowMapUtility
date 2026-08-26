import logging
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

import flowmaputility.logging_config as logging_config
from flowmaputility.builder import Builder
from flowmaputility.correlations.ansari import AnsariModel
from flowmaputility.correlations.beggs_brill import BeggsBrillModel
from flowmaputility.domain.validators import (
    FluidParamsValidator,
    PipeParamsValidator,
)
from flowmaputility.engine.manager import ProcessManager
from flowmaputility.grid.generator import GridGenerator
from flowmaputility.grid.info import GridInfo
from flowmaputility.logging_config import LOGGER_NAME
from flowmaputility.visualization.tuners import ColorTuner, GraphTuner


@pytest.fixture(autouse=True)
def _isolate_flowmaputility_logging(tmp_path, monkeypatch):
    """
    Изолирует глобальное состояние логгера "flowmaputility" между тестами.

    setup_logging() идемпотентна и хранит состояние на уровне модуля —
    без сброса первый тест, реально запустивший расчет (а значит и
    setup_logging), навсегда прикрепил бы обработчики и выставил
    propagate=False, ломая caplog в остальных тестах. Заодно уводим
    лог-файл во временную директорию, чтобы тесты не мусорили в репозитории.
    """
    monkeypatch.setattr(logging_config, "LOG_FILE", str(tmp_path / "test.log"))

    logger = logging.getLogger(LOGGER_NAME)
    original_handlers = logger.handlers[:]
    original_propagate = logger.propagate
    original_level = logger.level

    yield

    if logging_config._listener is not None:
        logging_config._listener.stop()
    logging_config._configured = False
    logging_config._queue = None
    logging_config._listener = None

    logger.handlers[:] = original_handlers
    logger.propagate = original_propagate
    logger.setLevel(original_level)


@pytest.fixture
def info_for_ansari_correlation():
    pipe = PipeParamsValidator(0.062, 0.00005, 90).validate()
    fluid = FluidParamsValidator(800, 50, 0.001, 0.00001, 0.01).validate()
    ansari_model = AnsariModel(pipe, fluid)
    return ansari_model


@pytest.fixture
def bb_model() -> BeggsBrillModel:
    # Диаметр трубы — 0.1 м, угол и параметры флюида этой моделью сейчас
    # не используются (см. get_pattern_code), но объекты обязательны по
    # контракту IFlowModel.__init__.
    pipe = PipeParamsValidator(0.1, 0.00005, 30.0).validate()
    fluid = FluidParamsValidator(800, 50, 0.001, 0.00001, 0.01).validate()
    return BeggsBrillModel(pipe, fluid)


@pytest.fixture
def creating_Pipe():
    pipe = Mock(angle=80.0)
    return pipe


@pytest.fixture
def creating_Pipe_Beggs_Brill():
    # Угол внутри диапазона Beggs-Brill (-90..75), но вне диапазона Ansari —
    # чтобы model.validate_angle() внутри creat_model() не падала.
    return Mock(angle=30.0)


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
    vsg_2d = vsg_1d[:, np.newaxis] * np.ones((3, 3))
    grid_info = GridInfo(vsl_1d, vsg_1d, vsl_2d, vsg_2d, 3, True)
    return ProcessManager(info_for_ansari_correlation, grid_info)


@pytest.fixture
def mock_plt():
    with patch("flowmaputility.visualization.tuners.plt") as mock:
        yield mock


@pytest.fixture
def mock_mcolors():
    with patch("flowmaputility.visualization.tuners.mcolors") as mock:
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


@pytest.fixture
def builder() -> Builder:
    builder = Builder()
    builder.pipe_params = MagicMock()
    builder.fluid_params = MagicMock()
    builder.system_params = MagicMock()

    builder.velocite_liquid = Mock()
    builder.velocite_gas = Mock()
    builder.resolution = Mock()
    builder.grid_info = MagicMock()
    builder.scale_flag = Mock()
    builder.grid_generator = MagicMock()

    builder.correlation_factory = MagicMock()
    builder.model = MagicMock()
    builder.model_name = Mock()

    builder.n_count = Mock()
    builder.run_core = MagicMock()

    builder.save_path = Mock()
    builder.show_plot = Mock()
    builder.show_progress = Mock()
    builder.vis_manadger = MagicMock()
    return builder
