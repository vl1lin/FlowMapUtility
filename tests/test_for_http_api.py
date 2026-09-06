"""
Тесты HTTP API (FastAPI TestClient).

Не путать с tests/test_for_api.py — тот файл, несмотря на имя,
тестирует Builder, а не HTTP-слой.
"""

import pytest
from fastapi.testclient import TestClient

from flowmaputility.api.main import app
from flowmaputility.builder import Builder
from flowmaputility.correlations.base import FlowPatternCode

client = TestClient(app)

_HAPPY_PATH_BODY = {
    "pipe": {"diameter": 0.062, "roughness": 0.00005, "angle": 90},
    "fluid": {
        "density_liquid": 800,
        "density_gas": 50,
        "viscosity_liquid": 0.001,
        "viscosity_gas": 0.00001,
        "surface_tension": 0.01,
    },
    "velocity_liquid": {"min": 0.1, "max": 0.5},
    "velocity_gas": {"min": 10, "max": 15},
    "resolution": 5,
}


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_models_endpoint() -> None:
    response = client.get("/models")
    assert response.status_code == 200
    body = response.json()
    assert "ansari" in body["models"]
    assert "beggs_brill" in body["models"]
    expected_codes = {str(code.value) for code in FlowPatternCode}
    assert expected_codes <= body["pattern_legend"].keys()


def test_calculate_happy_path_small_resolution() -> None:
    response = client.post("/calculate", json=_HAPPY_PATH_BODY)
    assert response.status_code == 200
    body = response.json()
    assert body["model_name"] == "Ansari"
    assert len(body["code_matrix"]) == 5
    assert all(len(row) == 5 for row in body["code_matrix"])
    known_codes = {code.value for code in FlowPatternCode}
    assert all(
        cell in known_codes for row in body["code_matrix"] for cell in row
    )
    assert len(body["grid"]["vsl"]) == 5


def test_calculate_unknown_model_returns_400() -> None:
    body = {**_HAPPY_PATH_BODY, "model": "not_a_real_model"}
    response = client.post("/calculate", json=body)
    assert response.status_code == 400
    assert "not_a_real_model" in response.json()["detail"]


def test_calculate_angle_outside_model_range_returns_400() -> None:
    body = {
        **_HAPPY_PATH_BODY,
        "pipe": {**_HAPPY_PATH_BODY["pipe"], "angle": 30},
        "model": "ansari",
    }
    response = client.post("/calculate", json=body)
    assert response.status_code == 400
    assert "Ansari" in response.json()["detail"]


def test_calculate_resolution_over_cap_returns_422() -> None:
    body = {**_HAPPY_PATH_BODY, "resolution": 100_000}
    response = client.post("/calculate", json=body)
    assert response.status_code == 422


def test_calculate_unexpected_error_returns_generic_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _boom(self: Builder) -> Builder:
        raise RuntimeError("something internal")

    monkeypatch.setattr(Builder, "build_core", _boom)
    response = client.post("/calculate", json=_HAPPY_PATH_BODY)
    assert response.status_code == 500
    assert "something internal" not in response.text
