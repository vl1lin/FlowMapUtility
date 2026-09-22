/**
 * Фасад расчёта карты режимов течения. Порт src/flowmaputility/builder.py,
 * упрощённый под нужды статического сайта: вместо цепочки set_.../build_...
 * методов Builder - одна функция calculate(params), совмещающая валидацию,
 * генерацию сетки, выбор модели и однопоточный расчёт.
 *
 * Форма входа/выхода намеренно повторяет контракт POST /calculate
 * из FastAPI-backend (src/flowmaputility/api, ветка dev) - тот же контракт,
 * под который уже написан существующий frontend (проект FlowMapFrontend).
 */

import { createModel } from "./correlations/factory.js";
import { calculateGrid } from "./engine.js";
import { generateGrid } from "./grid.js";
import { patternLegend } from "./patternCodes.js";
import { validateFluidParams, validatePipeParams } from "./validators.js";

/**
 * @typedef {Object} CalculateParams
 * @property {{diameter: number, roughness: number, angle: number}} pipe
 * @property {{densityLiquid: number, densityGas: number, viscosityLiquid: number,
 *             viscosityGas: number, surfaceTension: number}} fluid
 * @property {{min: number, max: number}} velocityLiquid
 * @property {{min: number, max: number}} velocityGas
 * @property {number} [resolution]
 * @property {boolean} [logScale]
 * @property {string | null} [model] имя модели, либо null - выбор автоматически по углу трубы
 * @property {(doneRows: number, totalRows: number) => void} [onProgress]
 */

/**
 * @typedef {Object} CalculateResult
 * @property {string} modelName
 * @property {import("./grid.js").GridInfo} grid
 * @property {number[][]} codeMatrix
 * @property {Record<number, string>} patternLegend
 */

/**
 * @param {CalculateParams} params
 * @returns {CalculateResult}
 */
export function calculate(params) {
  const pipe = validatePipeParams(params.pipe.diameter, params.pipe.roughness, params.pipe.angle);
  const fluid = validateFluidParams(
    params.fluid.densityLiquid,
    params.fluid.densityGas,
    params.fluid.viscosityLiquid,
    params.fluid.viscosityGas,
    params.fluid.surfaceTension
  );

  const grid = generateGrid(
    [params.velocityLiquid.min, params.velocityLiquid.max],
    [params.velocityGas.min, params.velocityGas.max],
    params.resolution ?? 100,
    params.logScale ?? true
  );

  const model = createModel(params.model ?? null, pipe, fluid);
  const codeMatrix = calculateGrid(model, grid, params.onProgress);

  return {
    modelName: /** @type {typeof import("./correlations/base.js").FlowModel} */ (
      model.constructor
    ).modelName,
    grid,
    codeMatrix,
    patternLegend: patternLegend(),
  };
}
