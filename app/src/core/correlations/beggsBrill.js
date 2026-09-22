/**
 * Механистическая модель Беггса-Брилла (упрощённая классификация режима,
 * без расчёта удержания и градиента давления) для горизонтальных и наклонных
 * труб (угол от 0 до 75, не включая 75).
 * Порт src/flowmaputility/correlations/beggs_brill.py.
 */

import { FlowPatternCode } from "../patternCodes.js";
import { FlowModel } from "./base.js";

const G = 9.81;

const FP_SEG = 0;
const FP_INT = 1;
const FP_DIST = 2;
const FP_TRANS = 3;

const FLOW_PATTERN_MAP = {
  [FP_SEG]: FlowPatternCode.STRATIFIED,
  [FP_TRANS]: FlowPatternCode.SLUG,
  [FP_INT]: FlowPatternCode.SLUG,
  [FP_DIST]: FlowPatternCode.DISPERSED_BUBBLE,
};

/** Наибольшее число, строго меньшее 75.0 (аналог math.nextafter(75.0, -inf)). */
const ANGLE_MAX_EXCLUSIVE_75 = 74.99999999999999;

export class BeggsBrillModel extends FlowModel {
  static get modelName() {
    return "Beggs-Brill";
  }

  static get angleLimit() {
    return [0.0, ANGLE_MAX_EXCLUSIVE_75];
  }

  /**
   * @param {number} vsl скорость жидкости, м/с
   * @param {number} vsg скорость газа, м/с
   * @returns {number}
   */
  getPatternCode(vsl, vsg) {
    if (vsl < 1e-9) return FlowPatternCode.SINGLE_GAS;
    if (vsg < 1e-9) return FlowPatternCode.SINGLE_LIQUID;

    const diameter = this.pipe.diameter;
    const vm = vsl + vsg;
    const lamL = vsl / vm;
    const nFr = vm ** 2 / (G * diameter);

    const fp = this._flowPattern(lamL, nFr);
    return FLOW_PATTERN_MAP[fp];
  }

  /**
   * Определение базового режима потока по карте Beggs-Brill.
   * @param {number} lamL безотрывное удержание жидкости (vsl / (vsl+vsg))
   * @param {number} nFr число Фруда смеси
   * @returns {number}
   */
  _flowPattern(lamL, nFr) {
    if (nFr >= 316.0 * lamL ** 0.302 || nFr >= 0.5 * lamL ** -6.738) {
      return FP_DIST;
    }
    if (nFr <= 0.000925 * lamL ** -2.468) {
      return FP_SEG;
    }
    if (nFr <= 0.1 * lamL ** -1.452) {
      return FP_TRANS;
    }
    return FP_INT;
  }
}
