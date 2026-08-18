import multiprocessing as mp
from typing import TYPE_CHECKING, Iterator

import numpy as np

from flowmaputility.engine.worker import init_worker, worker_function

if TYPE_CHECKING:
    from flowmaputility.correlations.base import IFlowModel
    from flowmaputility.grid.info import GridInfo


class ProcessManager:
    """
    Класс для управления процессами расчета кодов режима потока.
    :param worker_model: Модель для расчета кодов режима потока
    :param grid: Информация о сетке расчета
    :param n_workers: Количество рабочих процессов
    """

    def __init__(
        self, worker_model: "IFlowModel", grid: "GridInfo", n_workers: int | None = None
    ):
        self.worker_model = worker_model
        self.grid = grid
        self.n_workers = n_workers

    def run(self) -> np.ndarray:
        """
        Запускает расчет кодов режима потока
        """
        with mp.Pool(
            processes=self._count_workers(),
            initializer=init_worker,
            initargs=(self.worker_model,),
        ) as pool:
            results = pool.imap_unordered(worker_function, self._prepare_tasks())
            code_pattern_grid = np.zeros(
                [self.grid.resolution, self.grid.resolution], dtype=np.int32
            )
            for i, row in results:
                code_pattern_grid[i] = row

        return code_pattern_grid

    def _count_workers(self) -> int:
        """
        Определяет количесвто рабочих процессов
        """
        if self.n_workers is None:
            return max(1, mp.cpu_count() - 1)
        return self.n_workers

    def _prepare_tasks(self) -> Iterator[tuple[int, np.ndarray, np.ndarray]]:
        """
        Подготавливает задачи для расчета в процессах
        """
        tasks = (
            (i, self.grid.vsl_2d[i, :], self.grid.vsg_2d[i, :])
            for i in range(self.grid.resolution)
        )
        return tasks
