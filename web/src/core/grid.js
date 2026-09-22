/**
 * Генератор расчётной сетки скоростей (Vl x Vg). Порт
 * src/flowmaputility/grid/generator.py и grid/info.py.
 * Вместо numpy - обычные JS-массивы (vsl2d/vsg2d - массивы массивов).
 */

/**
 * @typedef {Object} GridInfo
 * @property {number[]} vsl1d 1D массив скоростей жидкости, м/с (по возрастанию)
 * @property {number[]} vsg1d 1D массив скоростей газа, м/с (по возрастанию)
 * @property {number[][]} vsl2d 2D массив [resolution][resolution], повторяет vsl1d по строкам
 * @property {number[][]} vsg2d 2D массив [resolution][resolution], столбец i = vsg1d развёрнутый (max сверху)
 * @property {number} resolution разрешение сетки
 * @property {boolean} logScale флаг логарифмической шкалы
 */

/**
 * @param {[number, number]} range
 * @returns {[number, number]} диапазон, где min < max (меняет местами при необходимости)
 */
function validateRange(range) {
  if (!Array.isArray(range) || range.length !== 2) {
    throw new Error("range must be a tuple of two numbers");
  }
  let [min, max] = range.map(Number);
  if (Number.isNaN(min) || Number.isNaN(max)) {
    throw new Error(`Диапазон должен быть парой чисел. Получено: ${range}`);
  }
  if (min > max) {
    console.warn(
      `Минимальное значение (${min}) должно быть строго меньше максимального (${max})\nМеняем местами`
    );
    [min, max] = [max, min];
  }
  return [min, max];
}

/**
 * numpy.linspace(min, max, resolution) с endpoint=True.
 * @param {number} min
 * @param {number} max
 * @param {number} resolution
 * @returns {number[]}
 */
function linspace(min, max, resolution) {
  if (resolution <= 1) return [min];
  const step = (max - min) / (resolution - 1);
  return Array.from({ length: resolution }, (_, i) => min + i * step);
}

/**
 * numpy.logspace(log10(min), log10(max), resolution) с endpoint=True.
 * @param {number} min
 * @param {number} max
 * @param {number} resolution
 * @returns {number[]}
 */
function logspace(min, max, resolution) {
  return linspace(Math.log10(min), Math.log10(max), resolution).map((v) => 10 ** v);
}

/**
 * Генерирует расчётную сетку скоростей.
 * @param {[number, number]} vslRangeInput диапазон скорости жидкости, м/с
 * @param {[number, number]} vsgRangeInput диапазон скорости газа, м/с
 * @param {number} [resolution=100] разрешение сетки (количество ячеек по каждой оси)
 * @param {boolean} [logScaleInput=true] использовать логарифмическую шкалу
 * @returns {GridInfo}
 */
export function generateGrid(vslRangeInput, vsgRangeInput, resolution = 100, logScaleInput = true) {
  const resolutionInt = Math.trunc(resolution);
  if (!Number.isFinite(resolutionInt)) {
    throw new Error(`resolution must be a number, got ${resolution}`);
  }
  if (typeof logScaleInput !== "boolean") {
    throw new TypeError("logScale must be a boolean");
  }

  const [vslMin, vslMax] = validateRange(vslRangeInput);
  const [vsgMin, vsgMax] = validateRange(vsgRangeInput);

  let logScale = logScaleInput;
  if (vslMin <= 0 || vsgMin <= 0) {
    console.warn("log_scale requires positive values, switching to linear scale");
    logScale = false;
  }

  const generate1d = (min, max) =>
    logScale ? logspace(min, max, resolutionInt) : linspace(min, max, resolutionInt);

  const vsl1d = generate1d(vslMin, vslMax);
  const vsg1d = generate1d(vsgMin, vsgMax);

  // vsl2d: каждая строка - копия vsl1d (np.ones((res,1)) * vsl1d)
  const vsl2d = Array.from({ length: resolutionInt }, () => vsl1d.slice());

  // vsg2d: столбец i - развёрнутый (reversed) vsg1d[i], постоянный по строке
  // (revese_vsg_1d[:, newaxis] * np.ones(resolution))
  const reversedVsg1d = vsg1d.slice().reverse();
  const vsg2d = reversedVsg1d.map((value) => Array(resolutionInt).fill(value));

  return { vsl1d, vsg1d, vsl2d, vsg2d, resolution: resolutionInt, logScale };
}
