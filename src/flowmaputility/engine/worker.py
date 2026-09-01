from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from flowmaputility.correlations.base import IFlowModel

_worker_model: "IFlowModel"


def init_worker(model: "IFlowModel"):
    """
    Сохраняет в памяти процесса объект модели для расчета кодов режима потока
    :param model: Модель для расчета кодов режима потока
    """
    global _worker_model
    _worker_model = model


def worker_function(args: tuple[int, np.ndarray, np.ndarray]) -> tuple[int, np.ndarray]:
    """
    Основная функция - воркер которая будет запускаться в процессах
    :param args: Кортеж с номером строки, массивами vsl и vsg
    """
    i, vsl, vsg = args
    results = np.zeros(len(vsl), dtype=np.int32)
    for j in range(len(vsl)):
        results[j] = _worker_model.get_pattern_code(vsl[j], vsg[j])

    return i, results
