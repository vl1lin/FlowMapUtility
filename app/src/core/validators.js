/**
 * Валидация исходных данных. Портировано из src/flowmaputility/domain/validators.py
 * и src/flowmaputility/domain/params.py.
 *
 * В отличие от Python-версии здесь нет отдельных dataclass-типов PipeParams/
 * FluidParams/SystemParams — валидатор просто возвращает обычный объект
 * с числовыми полями (typeof === "number", без NaN).
 */

/**
 * Проверяет, что значение - конечное число (не NaN, не Infinity, не boolean,
 * не строка). Бросает Error с именем поля, если проверка не пройдена.
 * @param {string} name
 * @param {*} value
 * @returns {number}
 */
function requireNumber(name, value) {
  if (typeof value !== "number" || Number.isNaN(value) || !Number.isFinite(value)) {
    throw new Error(`${name} must be number`);
  }
  return value;
}

/**
 * @param {Record<string, number>} fields
 * @returns {Record<string, number>} тот же объект, со значениями приведёнными к Number
 */
function validateFields(fields) {
  const result = {};
  for (const [name, value] of Object.entries(fields)) {
    result[name] = requireNumber(name, value);
  }
  return result;
}

/**
 * Валидатор параметров трубы.
 * @param {number} diameter диаметр сечения трубы, м
 * @param {number} roughness шероховатость трубы, м
 * @param {number} angle угол наклона трубы, градусы
 */
export function validatePipeParams(diameter, roughness, angle) {
  return validateFields({ diameter, roughness, angle });
}

/**
 * Валидатор параметров флюида (газожидкостной смеси).
 * @param {number} densityLiquid плотность жидкости, кг/м^3
 * @param {number} densityGas плотность газа, кг/м^3
 * @param {number} viscosityLiquid вязкость жидкости, Па*с
 * @param {number} viscosityGas вязкость газа, Па*с
 * @param {number} surfaceTension поверхностное натяжение, Н/м
 */
export function validateFluidParams(
  densityLiquid,
  densityGas,
  viscosityLiquid,
  viscosityGas,
  surfaceTension
) {
  return validateFields({
    densityLiquid,
    densityGas,
    viscosityLiquid,
    viscosityGas,
    surfaceTension,
  });
}

/**
 * Валидатор параметров системы (в расчёте режима течения сейчас не используются,
 * сохранены для паритета с Python API).
 * @param {number} pressure давление, Па
 * @param {number} temperature температура, К
 */
export function validateSystemParams(pressure, temperature) {
  return validateFields({ pressure, temperature });
}
