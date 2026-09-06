"""
Чистые функции, превращающие объекты пакета flowmaputility (Builder,
GridInfo, numpy-массивы, FlowPatternCode) в JSON-совместимые структуры.
"""

import numpy as np

from flowmaputility.api.schemas import GridInfoResponse
from flowmaputility.correlations.base import FlowPatternCode
from flowmaputility.correlations.factory import ModelFactory
from flowmaputility.grid.info import GridInfo


def grid_info_to_response(grid_info: GridInfo) -> GridInfoResponse:
    return GridInfoResponse(
        vsl=grid_info.vsl_1d.tolist(),
        vsg=grid_info.vsg_1d.tolist(),
        resolution=grid_info.resolution,
        log_scale=grid_info.log_scale,
    )


def code_matrix_to_list(code_matrix: np.ndarray) -> list[list[int]]:
    """
    .tolist() важен: без него в матрице остаются numpy.int32,
    которые json/Pydantic сериализовать не умеют.
    """
    return code_matrix.tolist()


def pattern_legend() -> dict[int, str]:
    return {code.value: code.name for code in FlowPatternCode}


def available_models() -> list[str]:
    return sorted(ModelFactory().MODELS.keys())
