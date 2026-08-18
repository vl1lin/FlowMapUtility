from typing import TYPE_CHECKING
from unittest.mock import Mock

import numpy as np
import pytest

from flowmaputility.engine.worker import init_worker, worker_function

if TYPE_CHECKING:
    from flowmaputility.engine.manager import ProcessManager


def test_core_run(core_beginer: "ProcessManager") -> None:
    manager: "ProcessManager" = core_beginer
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
