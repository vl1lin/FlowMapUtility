import logging
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import numpy as np
import pytest

from flowmaputility.engine.worker import init_worker, worker_function
from flowmaputility.logging_config import LOGGER_NAME

if TYPE_CHECKING:
    from flowmaputility.engine.manager import ProcessManager


def test_core_run(core_beginer: "ProcessManager") -> None:
    manager: "ProcessManager" = core_beginer
    with patch("flowmaputility.engine.manager.mp.cpu_count", return_value=8):
        assert manager._count_workers() == 7
    tasks = [
        (0, [0.1, 0.2, 0.3], [3.0 for _ in range(3)]),
        (1, [0.1, 0.2, 0.3], [2.0 for _ in range(3)]),
        (2, [0.1, 0.2, 0.3], [1.0 for _ in range(3)]),
    ]
    for tsk_my, tsk_manager in zip(tasks, manager._prepare_tasks()):
        i, vsl, vsg = tsk_my
        i_manager, vsl_manager, vsg_manager = tsk_manager
        assert i == i_manager
        assert np.allclose(vsl, vsl_manager)
        assert np.allclose(vsg, vsg_manager)


def test_worker_function() -> None:
    ansari = Mock(get_pattern_code=Mock(return_value=105))
    i: int = 0
    vsl = np.array([0.1 for _ in range(3)])
    vsg = np.array([1.0 for _ in range(3)])
    args = (i, vsl, vsg)
    init_worker(ansari)
    res_i, result = worker_function(args)
    assert res_i == i
    assert len(result) == 3
    assert np.all(result == 105)


def test_worker_function_logs_result_row(caplog) -> None:
    ansari = Mock(get_pattern_code=Mock(return_value=105))
    vsl = np.array([0.1, 0.2, 0.3])
    vsg = np.array([1.0, 1.0, 1.0])

    init_worker(ansari)  # log_queue=None -> логирование в воркере не настроено

    logger = logging.getLogger(LOGGER_NAME)
    logger.addHandler(caplog.handler)
    logger.setLevel(logging.DEBUG)
    try:
        with caplog.at_level(logging.DEBUG):
            worker_function((0, vsl, vsg))
    finally:
        logger.removeHandler(caplog.handler)

    assert "row=0" in caplog.text
    assert "[105, 105, 105]" in caplog.text


def test_for_core(core_beginer: "ProcessManager") -> None:
    manager: "ProcessManager" = core_beginer
    grid = [[105, 105, 105], [105, 105, 105], [103, 103, 103]]
    code_grid = manager.run()
    assert code_grid is not None
    assert code_grid.shape == (manager.grid.resolution, manager.grid.resolution)
    assert np.all(code_grid == np.array(grid))


if __name__ == "__main__":
    # Если ты запускаешь через pytest, он сам поймет эту конструкцию.
    # Если запускаешь просто python test_file.py, сработает этот блок.
    pytest.main([__file__])
