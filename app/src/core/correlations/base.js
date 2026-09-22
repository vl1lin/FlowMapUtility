/**
 * Базовый класс для всех моделей корреляции.
 * Портировано из src/flowmaputility/correlations/base.py (IFlowModel).
 */

/**
 * @typedef {{diameter: number, roughness: number, angle: number}} PipeParams
 * @typedef {{densityLiquid: number, densityGas: number, viscosityLiquid: number,
 *            viscosityGas: number, surfaceTension: number}} FluidParams
 */

export class FlowModel {
  /**
   * @param {PipeParams} pipe
   * @param {FluidParams} fluid
   */
  constructor(pipe, fluid) {
    if (new.target === FlowModel) {
      throw new TypeError("FlowModel — абстрактный класс, используйте наследника");
    }
    this.pipe = pipe;
    this.fluid = fluid;
  }

  /** Человеческое имя модели для UI и легенды. @returns {string} */
  static get modelName() {
    throw new Error("not implemented");
  }

  /** Допустимый диапазон углов в градусах. @returns {[number, number]} */
  static get angleLimit() {
    throw new Error("not implemented");
  }

  /**
   * Вычислить режим течения для одной точки.
   * @param {number} vsl скорость жидкости, м/с
   * @param {number} vsg скорость газа, м/с
   * @returns {number} код режима течения (FlowPatternCode)
   */
  // eslint-disable-next-line no-unused-vars
  getPatternCode(vsl, vsg) {
    throw new Error("not implemented");
  }

  /**
   * Валидировать угол течения против допустимого диапазона модели.
   * @throws {Error} если угол выходит за допустимый диапазон
   */
  validateAngle() {
    const [min, max] = /** @type {typeof FlowModel} */ (this.constructor).angleLimit;
    if (this.pipe.angle < min || this.pipe.angle > max) {
      throw new Error(
        `Модель '${/** @type {typeof FlowModel} */ (this.constructor).modelName}' ` +
          `работает только для углов ${min}°-${max}°.\n` +
          `Текущий угол: ${this.pipe.angle}°`
      );
    }
  }
}
