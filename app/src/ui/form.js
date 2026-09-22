/**
 * Логика формы: чтение/валидация полей, вызов расчёта и экспорта.
 * Адаптировано из FlowMapFrontend/form.js — тот же набор полей формы,
 * но вместо fetch к backend вызывается core/calculator.js прямо в браузере.
 */

import { availableModels } from "../core/correlations/factory.js";
import { calculate } from "../core/calculator.js";
import { exportGrid } from "../core/gridExporter.js";
import { patternLegend } from "../core/patternCodes.js";
import { renderHeatmap, renderLegend } from "./chart.js";

/** Последний успешный результат расчёта — нужен для экспорта. */
let lastResult = null;

function setLoading(isLoading) {
  const btn = document.getElementById("calculate-btn");
  btn.disabled = isLoading;
  btn.textContent = isLoading ? "Считаем..." : "Рассчитать";
}

function showError(message) {
  const el = document.getElementById("error");
  el.textContent = message || "";
  el.hidden = !message;
}

function readFormValues() {
  const num = (id) => parseFloat(document.getElementById(id).value);
  return {
    diameter: num("diameter"),
    roughness: num("roughness"),
    angle: num("angle"),
    density_liquid: num("density_liquid"),
    density_gas: num("density_gas"),
    viscosity_liquid: num("viscosity_liquid"),
    viscosity_gas: num("viscosity_gas"),
    surface_tension: num("surface_tension"),
    vl_min: num("vl_min"),
    vl_max: num("vl_max"),
    vg_min: num("vg_min"),
    vg_max: num("vg_max"),
    resolution: parseInt(document.getElementById("resolution").value, 10),
    log_scale: document.getElementById("log_scale").checked,
    invert_axes: document.getElementById("invert_axes").checked,
    model: document.getElementById("model").value || null,
  };
}

function validateForm(values) {
  const requiredFields = [
    "diameter", "roughness", "angle",
    "density_liquid", "density_gas",
    "viscosity_liquid", "viscosity_gas", "surface_tension",
    "vl_min", "vl_max", "vg_min", "vg_max", "resolution",
  ];

  for (const field of requiredFields) {
    if (Number.isNaN(values[field])) {
      return "Заполните все поля";
    }
  }

  const positiveFields = [
    "diameter", "density_liquid", "density_gas",
    "viscosity_liquid", "viscosity_gas", "surface_tension",
    "vl_min", "vl_max", "vg_min", "vg_max",
  ];
  for (const field of positiveFields) {
    if (values[field] <= 0) {
      return "Значения должны быть положительными";
    }
  }

  if (values.resolution < 2 || values.resolution > 1000) {
    return "Resolution должен быть от 2 до 1000";
  }

  if (values.vl_min >= values.vl_max) {
    return "Минимум скорости жидкости должен быть меньше максимума";
  }

  if (values.vg_min >= values.vg_max) {
    return "Минимум скорости газа должен быть меньше максимума";
  }

  return null;
}

function buildCalculateParams(values) {
  return {
    pipe: { diameter: values.diameter, roughness: values.roughness, angle: values.angle },
    fluid: {
      densityLiquid: values.density_liquid,
      densityGas: values.density_gas,
      viscosityLiquid: values.viscosity_liquid,
      viscosityGas: values.viscosity_gas,
      surfaceTension: values.surface_tension,
    },
    velocityLiquid: { min: values.vl_min, max: values.vl_max },
    velocityGas: { min: values.vg_min, max: values.vg_max },
    resolution: values.resolution,
    logScale: values.log_scale,
    model: values.model,
  };
}

export function populateModels() {
  const select = document.getElementById("model");

  const autoOption = document.createElement("option");
  autoOption.value = "";
  autoOption.textContent = "Автоматически";
  select.appendChild(autoOption);

  for (const model of availableModels()) {
    const option = document.createElement("option");
    option.value = model;
    option.textContent = model;
    select.appendChild(option);
  }
}

function handleCalculate() {
  showError(null);
  const values = readFormValues();
  const validationError = validateForm(values);
  if (validationError) {
    showError(validationError);
    return;
  }

  setLoading(true);
  // Расчёт синхронный и однопоточный - даём браузеру перерисовать кнопку
  // ("Считаем...") перед тем, как заблокировать поток вычислением.
  setTimeout(() => {
    try {
      const result = calculate(buildCalculateParams(values));
      lastResult = result;
      renderHeatmap(result.grid, result.codeMatrix, values.invert_axes);
      renderLegend(result.patternLegend);
      document.getElementById("export-fieldset").hidden = false;
    } catch (e) {
      showError(e.message);
    } finally {
      setLoading(false);
    }
  }, 0);
}

function handleExport() {
  if (!lastResult) return;
  const format = document.getElementById("export-format").value;
  try {
    exportGrid(lastResult.grid, lastResult.codeMatrix, `flow_map.${format}`);
  } catch (e) {
    showError(e.message);
  }
}

export function initForm() {
  populateModels();
  renderLegend(patternLegend());
  document.getElementById("calculate-btn").addEventListener("click", handleCalculate);
  document.getElementById("export-btn").addEventListener("click", handleExport);
}
