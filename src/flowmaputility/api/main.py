"""
FastAPI-приложение: маршруты + перевод ошибок пакета flowmaputility в HTTP-коды.
"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from flowmaputility.api import serializers
from flowmaputility.api.schemas import (
    CalculateRequest,
    CalculateResponse,
    HealthResponse,
    ModelsResponse,
)
from flowmaputility.builder import Builder

app = FastAPI(title="FlowMapUtility API")

# Список разрешённых origin'ов задаётся переменной окружения (домен
# frontend-репозитория ещё не известен на момент написания кода, и его
# может понадобиться сменить без правки кода). Пусто по умолчанию — CORS
# ничего не разрешает, пока origin явно не указан.
_allowed_origins = [
    origin.strip()
    for origin in os.getenv("FLOWMAP_API_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=False,
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/models", response_model=ModelsResponse)
def models() -> ModelsResponse:
    return ModelsResponse(
        models=serializers.available_models(),
        pattern_legend=serializers.pattern_legend(),
    )


@app.post("/calculate", response_model=CalculateResponse)
def calculate(payload: CalculateRequest) -> CalculateResponse:
    """
    Синхронный (не async def) обработчик: расчёт блокирующий
    (multiprocessing.Pool внутри ProcessManager). FastAPI сам выполнит
    его в threadpool, не блокируя event loop.
    """
    builder = Builder()
    try:
        builder = (
            builder.set_pipe_params(
                payload.pipe.diameter, payload.pipe.roughness, payload.pipe.angle
            )
            .set_fluid_params(
                payload.fluid.density_liquid,
                payload.fluid.density_gas,
                payload.fluid.viscosity_liquid,
                payload.fluid.viscosity_gas,
                payload.fluid.surface_tension,
            )
            .set_velocite_liquid(
                payload.velocity_liquid.min, payload.velocity_liquid.max
            )
            .set_velocite_gas(payload.velocity_gas.min, payload.velocity_gas.max)
            .set_resolution(payload.resolution)
            .set_scale_flag(payload.log_scale)
        )
        if payload.model is not None:
            builder = builder.set_model(payload.model)

        # На бесплатном тарифе хостинга — всегда 1 воркер, клиент это
        # число не выбирает (риск перегрузки единственного инстанса).
        builder = (
            builder.set_count_of_workers(1)
            .build_grid_generator()
            .build_grid_info()
            .build_model_factory()
            .build_model()
            .build_core()
        )
        code_matrix = builder.run_core.run()  # type: ignore[union-attr]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка расчёта"
        ) from e

    return CalculateResponse(
        model_name=builder.model.name(),  # type: ignore[union-attr]
        grid=serializers.grid_info_to_response(builder.grid_info),  # type: ignore[arg-type]
        code_matrix=serializers.code_matrix_to_list(code_matrix),
        pattern_legend=serializers.pattern_legend(),
    )
