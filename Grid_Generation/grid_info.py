from typing import NamedTuple

import numpy as np


class GridInfo(NamedTuple):
    """
    Структура данных для хранения информации о сетке.

    Attributes:
        vsl_1d: 1D массив скоростей по оси vsl.
        vsg_1d: 1D массив скоростей по оси vsg.
        vsl_2d: 2D массив скоростей по оси vsl.
        vsg_2d: 2D массив скоростей по оси vsg.
        resolution: Разрешение сетки.
        log_scale: Флаг использования логарифмической шкалы.
    """

    vsl_1d: np.ndarray
    vsg_1d: np.ndarray
    vsl_2d: np.ndarray
    vsg_2d: np.ndarray
    resolution: int
    log_scale: bool
