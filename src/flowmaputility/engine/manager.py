import logging
import multiprocessing as mp
from typing import TYPE_CHECKING, Iterator

import numpy as np
from tqdm import tqdm

from flowmaputility.engine.worker import init_worker, worker_function
from flowmaputility.logging_config import (
    LOGGER_NAME,
    get_log_queue,
    start_queue_listener,
)

if TYPE_CHECKING:
    from flowmaputility.correlations.base import IFlowModel
    from flowmaputility.grid.info import GridInfo

_logger = logging.getLogger(LOGGER_NAME)


class ProcessManager:
    """
    Класс для управления процессами расчета кодов режима потока.
    :param worker_model: Модель для расчета кодов режима потока
    :param grid: Информация о сетке расчета
    :param n_workers: Количество рабочих процессов
    :param show_progress: Показывать ли прогресс-бар расчета (по умолчанию выключен)
    """

    def __init__(
        self,
        worker_model: "IFlowModel",
        grid: "GridInfo",
        n_workers: int | None = None,
        show_progress: bool = False,
    ):
        self.worker_model = worker_model
        self.grid = grid
        self.n_workers = n_workers
        self.show_progress = show_progress

    def run(self) -> np.ndarray:
        """
        Запускает расчет кодов режима потока
        """
        log_queue = get_log_queue()
        n_workers = self._count_workers()

        _logger.info(
            "Расчёт начат: модель=%s, сетка=%dx%d, воркеров=%d",
            self.worker_model.name(),
            self.grid.resolution,
            self.grid.resolution,
            n_workers,
        )

        with mp.Pool(
            processes=n_workers,
            initializer=init_worker,
            initargs=(self.worker_model, log_queue),
        ) as pool:
            # Поток-слушатель очереди логов стартует только теперь, когда
            # воркеры уже forked — иначе форкался бы процесс с лишним
            # живым потоком (см. logging_config.start_queue_listener).
            start_queue_listener()
            results = pool.imap_unordered(worker_function, self._prepare_tasks())
            code_pattern_grid = np.zeros(
                [self.grid.resolution, self.grid.resolution], dtype=np.int32
            )
            for i, row in tqdm(
                results,
                total=self.grid.resolution,
                desc="Расчёт карты режимов",
                disable=not self.show_progress,
            ):
                code_pattern_grid[i] = row

        _logger.info("Расчёт завершён")

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
