"""
Pydantic-модели запросов и ответов HTTP API.
"""

import os

from pydantic import BaseModel, Field

# Кап на разрешение сетки — защита бесплатного хостинга (1 воркер) от
# слишком тяжёлых расчётов. Читается один раз при импорте модуля.
MAX_RESOLUTION = int(os.getenv("FLOWMAP_API_MAX_RESOLUTION", "150"))


class PipeParamsRequest(BaseModel):
    """Параметры трубы. Единицы СИ: м, м, градусы."""

    diameter: float = Field(gt=0)
    roughness: float = Field(ge=0)
    angle: float


class FluidParamsRequest(BaseModel):
    """Параметры флюида. Единицы СИ: кг/м³, кг/м³, Па·с, Па·с, Н/м."""

    density_liquid: float = Field(gt=0)
    density_gas: float = Field(gt=0)
    viscosity_liquid: float = Field(gt=0)
    viscosity_gas: float = Field(gt=0)
    surface_tension: float = Field(gt=0)


class VelocityRangeRequest(BaseModel):
    """Диапазон скорости (ось сетки), м/с."""

    min: float = Field(ge=0)
    max: float = Field(gt=0)


class CalculateRequest(BaseModel):
    """Тело запроса POST /calculate."""

    pipe: PipeParamsRequest
    fluid: FluidParamsRequest
    velocity_liquid: VelocityRangeRequest
    velocity_gas: VelocityRangeRequest
    resolution: int = Field(default=100, ge=2, le=MAX_RESOLUTION)
    log_scale: bool = True
    model: str | None = None  # None -> Builder сам выбирает модель по углу трубы


class GridInfoResponse(BaseModel):
    vsl: list[float]
    vsg: list[float]
    resolution: int
    log_scale: bool


class CalculateResponse(BaseModel):
    model_name: str
    grid: GridInfoResponse
    code_matrix: list[list[int]]
    pattern_legend: dict[int, str]


class ModelsResponse(BaseModel):
    models: list[str]
    pattern_legend: dict[int, str]


class HealthResponse(BaseModel):
    status: str
