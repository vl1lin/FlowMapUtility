import logging
import multiprocessing as mp
from typing import TYPE_CHECKING

import numpy as np

from flowmaputility.logging_config import LOGGER_NAME, configure_worker_logging

if TYPE_CHECKING:
    from flowmaputility.correlations.base import IFlowModel

_worker_model: "IFlowModel"
_logger = logging.getLogger(LOGGER_NAME)


def init_worker(model: "IFlowModel", log_queue: "mp.Queue | None" = None) -> None:
    """
    Сохраняет в памяти процесса объект модели для расчета кодов режима потока
    и настраивает логирование воркера через общую очередь.
    :param model: Модель для расчета кодов режима потока
    :param log_queue: Очередь логов основного процесса (см. logging_config)
    """
    global _worker_model
    _worker_model = model
    configure_worker_logging(log_queue)


def worker_function(args: tuple[int, np.ndarray, np.ndarray]) -> tuple[int, np.ndarray]:
    """
    Основная функция - воркер которая будет запускаться в процессах
    :param args: Кортеж с номером строки, массивами vsl и vsg
    """
    i, vsl, vsg = args
    results = np.zeros(len(vsl), dtype=np.int32)
    for j in range(len(vsl)):
        results[j] = _worker_model.get_pattern_code(vsl[j], vsg[j])

    _logger.debug(
        "row=%d vsl_range=(%s, %s) vsg_range=(%s, %s) result=%s",
        i,
        vsl.min(),
        vsl.max(),
        vsg.min(),
        vsg.max(),
        results.tolist(),
    )

    return i, results
