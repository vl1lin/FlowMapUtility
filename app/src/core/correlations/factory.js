/**
 * Фабрика для создания моделей расчёта режима потока.
 * Порт src/flowmaputility/correlations/factory.py.
 */

import { AnsariModel } from "./ansari.js";
import { BeggsBrillModel } from "./beggsBrill.js";

/** @type {Record<string, typeof import("./base.js").FlowModel>} */
export const MODELS = {
  ansari: AnsariModel,
  beggs_brill: BeggsBrillModel,
};

/**
 * Приводит имя модели к нижнему регистру, заменяет пробелы и дефисы
 * на подчёркивания (единый стиль именования моделей в словаре MODELS).
 * @param {string} modelName
 * @returns {string}
 */
export function parseModelName(modelName) {
  return modelName.toLowerCase().replace(/[-\s]/g, "_");
}

/** @returns {string[]} отсортированный список поддерживаемых имён моделей */
export function availableModels() {
  return Object.keys(MODELS).sort();
}

/**
 * Создаёт модель расчёта режима потока по имени или по углу трубы.
 * @param {string | number | null | undefined} modelNameOrAngle имя модели,
 *   угол в градусах, или null/undefined - выбор модели автоматически по углу трубы
 * @param {import("./base.js").PipeParams} pipe
 * @param {import("./base.js").FluidParams} fluid
 * @returns {import("./base.js").FlowModel}
 */
export function createModel(modelNameOrAngle, pipe, fluid) {
  if (modelNameOrAngle === null || modelNameOrAngle === undefined) {
    return createModel(pipe.angle, pipe, fluid);
  }

  if (typeof modelNameOrAngle === "string") {
    const ModelClass = MODELS[parseModelName(modelNameOrAngle)];
    if (!ModelClass) {
      throw new Error(`Model ${modelNameOrAngle} is not supported`);
    }
    const model = new ModelClass(pipe, fluid);
    model.validateAngle();
    return model;
  }

  if (typeof modelNameOrAngle === "number") {
    for (const ModelClass of Object.values(MODELS)) {
      const [min, max] = ModelClass.angleLimit;
      if (modelNameOrAngle >= min && modelNameOrAngle <= max) {
        return new ModelClass(pipe, fluid);
      }
    }
    throw new Error(`Angle ${modelNameOrAngle} is out of range for any model`);
  }

  throw new TypeError(`Expected string or number, got ${typeof modelNameOrAngle}`);
}
