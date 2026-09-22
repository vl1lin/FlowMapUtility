/**
 * Модель Ансари для расчёта режима потока (наклонные/вертикальные трубы, 75-90°).
 * Построчный порт src/flowmaputility/correlations/ansari.py — порядок операций
 * и имена переменных намеренно сохранены как в оригинале, чтобы численное
 * поведение (в т.ч. итеративный решатель _dbtran) совпадало 1-в-1 с Python.
 */

import { FlowPatternCode } from "../patternCodes.js";
import { FlowModel } from "./base.js";

const G = 9.81;

export class AnsariModel extends FlowModel {
  static get modelName() {
    return "Ansari";
  }

  static get angleLimit() {
    return [75.0, 90.0];
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
    const angle = this.pipe.angle;
    const relativeRoughness = this.pipe.roughness / diameter;
    const densityLiquid = this.fluid.densityLiquid;
    const densityGas = this.fluid.densityGas;
    const viscosityLiquid = this.fluid.viscosityLiquid;
    const viscosityGas = this.fluid.viscosityGas;
    const surfaceTension = this.fluid.surfaceTension;

    return this._fpup(
      vsl,
      vsg,
      diameter,
      relativeRoughness,
      densityLiquid,
      densityGas,
      viscosityLiquid,
      viscosityGas,
      angle,
      surfaceTension
    );
  }

  /**
   * Граничные скорости перехода в рассеянно-пузырьковый режим.
   * @returns {[number, number]} [vsl, vsg]
   */
  _dbtran(hgg, vsg, di, ed, denl, deng, vislPas, visgPas, ang, surl) {
    const c =
      2.0 *
      Math.sqrt((0.4 * surl) / ((denl - deng) * G)) *
      Math.pow(denl / surl, 0.6) *
      Math.pow(2.0 / di, 0.4);
    let vme = vsg + 1.5;
    let vsl = 0.0;
    let vmc = vme;

    for (let iter = 0; iter < 51; iter++) {
      let hg;
      if (hgg === 0.0) {
        hg = vsg / vme;
      } else {
        hg = hgg;
        vsg = hg * vme;
        vsl = vme - vsg;
      }
      const rhom = denl * (1.0 - hg) + deng * hg;
      const vism = vislPas * (1.0 - hg) + visgPas * hg;
      const re = vism > 0 ? (di * rhom * vme) / vism : 0.0;
      const ffm = this._frictionFactor(re, ed);
      const denom = c * Math.pow(ffm / 4.0, 0.4);
      if (denom === 0.0) {
        break;
      }
      vmc = Math.pow((0.725 + 4.15 * Math.sqrt(hg)) / denom, 0.8333);
      const ratio = vme > 0 ? vmc / vme : 1.0;
      if (ratio >= 0.99 && ratio <= 1.01) {
        break;
      }
      vme = (vmc + vme) / 2.0;
    }
    const vm = (vmc + vme) / 2.0;
    vsl = vm * (1.0 - hgg);
    if (hgg > 0.0) {
      vsg = vm * hgg;
    }
    return [vsl, vsg];
  }

  /**
   * Граничные точки переходов режима течения.
   * @returns {[number, number, number, number, number, number, number]}
   *   [vsgo, vsg1, vsl1, vsg2, vsl2, vsg3, vsl3]
   */
  _mpoint(di, ed, denl, deng, vislPas, visgPas, ang, surl) {
    const alfa = 0.0174533 * ang;
    const dmin = 19.0 * Math.sqrt(((denl - deng) * surl) / (denl ** 2 * G));

    let vsgo;
    if (ang > 70.0 && di > dmin * 0.95) {
      const vslTmp = 0.001;
      vsgo =
        (vslTmp +
          1.15 * Math.pow((G * (denl - deng) * surl) / denl ** 2, 0.25) * Math.sin(alfa)) /
        3.0;
    } else {
      vsgo = -1.0;
    }

    const vsg3 =
      (3.1 * Math.pow(surl * G * Math.sin(alfa) * (denl - deng), 0.25)) / Math.sqrt(deng);

    let vsg1 = -1.0;
    let vsl1 = -1.0;
    if (vsgo > 0.0) {
      [vsl1, vsg1] = this._dbtran(0.25, -1.0, di, ed, denl, deng, vislPas, visgPas, ang, surl);
    }

    let vsg2 = 0.2;
    let vsl2;
    [vsl2, vsg2] = this._dbtran(0.76, vsg2, di, ed, denl, deng, vislPas, visgPas, ang, surl);

    let vsl3 = 0.0;
    if (vsg2 >= vsg3) {
      vsg2 = vsg3;
      [vsl2] = this._dbtran(0.0, vsg2, di, ed, denl, deng, vislPas, visgPas, ang, surl);
      vsl3 = vsl2;
      if (vsg1 < vsg2) {
        return [vsgo, vsg1, vsl1, vsg2, vsl2, vsg3, vsl3];
      }
      vsg1 = vsg2;
      return [vsgo, vsg1, vsl1, vsg2, vsl2, vsg3, vsl3];
    }

    vsl3 = vsg3 / 0.76 - vsg3;
    return [vsgo, vsg1, vsl1, vsg2, vsl2, vsg3, vsl3];
  }

  /**
   * Определить режим течения для восходящего наклонного/вертикального потока.
   * @returns {number} код режима течения
   */
  _fpup(vsl, vsg, di, ed, denl, deng, vislPas, visgPas, ang, surl) {
    const alfa = 0.0174533 * ang;
    const [vsgo, , , vsg2, , vsg3] = this._mpoint(
      di,
      ed,
      denl,
      deng,
      vislPas,
      visgPas,
      ang,
      surl
    );

    if (vsg >= vsg3) {
      return FlowPatternCode.ANNULAR;
    }

    if (vsg <= vsg2) {
      const [vslb] = this._dbtran(0.0, vsg, di, ed, denl, deng, vislPas, visgPas, ang, surl);
      if (vsl < vslb) {
        if (vsgo > 0.0) {
          const vsgb =
            (vsl +
              1.15 * Math.pow((G * (denl - deng) * surl) / denl ** 2, 0.25) * Math.sin(alfa)) /
            3.0;
          return vsg > vsgb ? FlowPatternCode.SLUG : FlowPatternCode.BUBBLE;
        }
        return FlowPatternCode.SLUG;
      }
      return FlowPatternCode.DISPERSED_BUBBLE;
    }

    const vslb = vsg / 0.76 - vsg;
    return vsl >= vslb ? FlowPatternCode.DISPERSED_BUBBLE : FlowPatternCode.SLUG;
  }

  /**
   * Коэффициент трения Муди (Дарси-Вейсбаха), явная аппроксимация Бркича уравнения Колбрука.
   * @param {number} nRe число Рейнольдса
   * @param {number} roughnessD относительная шероховатость трубы (eps/d)
   * @returns {number}
   */
  _frictionFactor(nRe, roughnessD) {
    if (nRe === 0.0) return 0.0;
    if (nRe < 2000.0) return 64.0 / nRe;
    const s = Math.log(nRe / (1.816 * Math.log((1.1 * nRe) / Math.log(1.0 + 1.1 * nRe))));
    const f1 = -2.0 * Math.log10(roughnessD / 3.71 + (2.0 * s) / nRe);
    return 1.0 / f1 ** 2;
  }
}
