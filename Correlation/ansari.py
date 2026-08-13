import math

from Correlation.model_abs import FlowPatternCode, IFlowModel
from Data_Block_1.data import FluidParams, PipeParams

_MAXIT = 100  # Максимальное количество итераций


class AnsariModel(IFlowModel):
    """
    Модель Ансаря для расчета режима потока.
    :param pipe: Объект PipeParams, в котором информация о трубе
    :param fluid: Объект FluidParams, в котором информация о свойствах флюидов в потоке
    """

    def __init__(self, pipe: PipeParams, fluid: FluidParams):
        super().__init__(pipe, fluid)

    @classmethod
    def name(cls) -> str:
        """
        Метод класса, возвращает имя модели
        """
        return "Ansari"

    @classmethod
    def angle_limit(cls) -> tuple[float, float]:
        """
        Метод класса, возвращает допустимый диапазон углов в градусах (min, max)
        """
        return (75.0, 90.0)

    def get_pattern_code(self, vsl: float, vsg: float) -> int:
        """
        Рассчитывает режим потока по значениям скоростей жидкости и газа
        :param vsl: Скорость жидкости в м/c
        :param vsg: Скорость газа в м/c
        """
        if vsl < 1e-9:
            return FlowPatternCode.SINGLE_GAS.value
        if vsg < 1e-9:
            return FlowPatternCode.SINGLE_LIQUID.value

        diameter = self.pipe.diameter
        angle = self.pipe.angle
        roughness = self.pipe.roughness
        density_liquid = self.fluid.density_liquid
        density_gas = self.fluid.density_gas
        viscosity_liquid = self.fluid.viscosity_liquid
        viscosity_gas = self.fluid.viscosity_gas
        surface_tension = self.fluid.surface_tension

        pattern_code = self._fpup(
            vsl,
            vsg,
            diameter,
            roughness,
            density_liquid,
            density_gas,
            viscosity_liquid,
            viscosity_gas,
            angle,
            surface_tension,
        )
        return pattern_code

    def _func(self, a, b, c, d, e, g, i, x):
        """
        Вычислить функцию и производную для итерации itsafe.

        :param i: селектор случая (1-5). Type: int
        :param x: текущее приближение. Type: float
        :return: (f, df). Type: tuple
        """
        if i == 1:
            an = 0.5
            f = c * x**an + 1.2 * (a + b) - b / (1.0 - x)
            df = an * c * x ** (an - 1.0) - b / (1.0 - x) ** 2
        elif i == 2:
            t2 = math.sqrt(9.81 * g * (1.0 - math.sqrt(max(x, 1e-15))))
            t3 = 1.0 - x
            t4 = 1.0 - e
            t5 = 9.961 * t2
            t6 = c - (c + t5) * t3 / t4
            t7 = 1.2 * (a + b) + d * t4**0.5
            if e > 0.25:
                t7 = t6
            t8 = c * (1.0 - e / x) + t7 * e / x
            t9 = t6 * t4 - a
            t10 = t5 * t3 + t6 * t4
            t11 = b - e * t7
            t12 = x * t8 - e * t7
            t13 = t9 / t10
            t14 = t11 / t12
            f = t13 - t14
            dt2 = -0.25 * 9.81 * g / t2 / math.sqrt(max(x, 1e-15))
            dt5 = 9.961 * dt2
            dt6 = -(dt5 * t3 / t4 - (c + t5) / t4)
            dt7 = 0.0
            if e > 0.25:
                dt7 = dt6
            dt8 = c * (e / x**2) + dt7 * e / x - t7 * e / x**2
            dt9 = dt6 * t4
            dt10 = dt5 * t3 - t5 + dt6 * t4
            dt11 = -e * dt7
            dt12 = t8 + x * dt8 - e * dt7
            dt13 = dt9 / t10 - t9 * dt10 / t10**2
            dt14 = dt11 / t12 - t11 * dt12 / t12**2
            df = dt13 - dt14
        elif i == 3:
            t1 = e / (0.425 + 2.65 * (d + e))
            t2 = (1.0 - 2.0 * x / a) ** 2
            t3 = (b * t2 - (b - c) * t1) / t2
            t4 = (t3 * t2 - (d + e)) / (1.0 - t2)
            f = x**3 - 0.75 * a * g * t4 * (1.0 - t2)
            dt2 = -4.0 * (1.0 - 2.0 * x / a) / a
            dt3 = (b - c) * t1 * dt2 / t2**2
            dt4 = (dt3 * t2 + t3 * dt2) / (1.0 - t2) + (t3 * t2 - (d + e)) * dt2 / (
                1.0 - t2
            ) ** 2
            df = 3.0 * x**2 - 0.75 * a * g * (dt4 * (1.0 - t2) - t4 * dt2)
        elif i == 4:
            t1 = 4.0 * x * (1.0 - x)
            z = 1.0 + c * x
            dt1 = 4.0 * (1.0 - 2.0 * x)
            dz = c
            f = b - z / t1 / (1.0 - t1) ** 2.5 + a / t1**3
            df = (
                -dz / t1 / (1.0 - t1) ** 2.5
                - 2.5 * z * dt1 / t1 / (1.0 - t1) ** 3.5
                + z * dt1 / t1**2 / (1.0 - t1) ** 2.5
                - 3.0 * a / t1**4 * dt1
            )
        else:  # i == 5
            t1 = 1.0 - (1.0 - 2.0 * x) ** 2
            dt1 = 4.0 * (1.0 - 2.0 * x)
            if abs(t1) < 1e-12 or abs(1.0 / t1 - 1.5) < 1e-12:
                x += 0.001
                t1 = 1.0 - (1.0 - 2.0 * x) ** 2
                dt1 = 4.0 * (1.0 - 2.0 * x)
            f = b - (2.0 - 1.5 * t1) * a / t1**3 / (1.0 - 1.5 * t1)
            df = (
                1.5 * dt1 * a / t1**3 / (1.0 - 1.5 * t1)
                + 3.0
                * a
                * dt1
                * (1.0 - 2.0 * t1)
                * (2.0 - 1.5 * t1)
                / t1**4
                / (1.0 - 1.5 * t1) ** 2
            )
        return f, df

    def _itsafe(self, a, b, c, d, e, g, i, x1, x2, xacc):
        """
        Безопасная итерация Ньютона-Рафсона в границах [x1, x2].

        :param i: селектор функции. Type: int
        :param x1: нижняя граница. Type: float
        :param x2: верхняя граница. Type: float
        :param xacc: допуск сходимости. Type: float
        :return: корень функции i. Type: float
        """
        fl, _ = self._func(a, b, c, d, e, g, i, x1)
        fh, _ = self._func(a, b, c, d, e, g, i, x2)
        if fl < 0.0:
            xl, xh = x1, x2
        else:
            xl, xh = x2, x1
            fl, fh = fh, fl

        result = 0.5 * (x1 + x2)
        dxold = abs(x2 - x1)
        dx = dxold
        f, df = self._func(a, b, c, d, e, g, i, result)

        for _ in range(_MAXIT):
            if ((result - xh) * df - f) * ((result - xl) * df - f) >= 0.0 or abs(
                2.0 * f
            ) > abs(dxold * df):
                dxold = dx
                dx = 0.5 * (xh - xl)
                result = xl + dx
                if xl == result:
                    return result
            else:
                dxold = dx
                dx = f / df
                temp = result
                result -= dx
                if temp == result:
                    return result
            if abs(dx) < xacc or abs(f) < xacc:
                return result
            f, df = self._func(a, b, c, d, e, g, i, result)
            if f < 0.0:
                xl = result
            else:
                xh = result
            if f == 0.0:
                return result
        return result

    def _dbtran(self, hgg, vsg, di, ed, denl, deng, visl_pas, visg_pas, ang, surl):
        """
        Граничные скорости перехода в рассеянно-пузырьковый режим.

        :return: (vsl, vsg). Type: tuple
        """
        c = (
            2.0
            * ((0.4 * surl) / ((denl - deng) * 9.81)) ** 0.5
            * (denl / surl) ** 0.6
            * (2.0 / di) ** 0.4
        )
        vme = vsg + 1.5
        vsl = 0.0
        vmc = vme
        ratio = 1.0
        for _ in range(51):
            if hgg == 0.0:
                hg = vsg / vme
            else:
                hg = hgg
                vsg = hg * vme
                vsl = vme - vsg
            rhom = denl * (1.0 - hg) + deng * hg
            vism = visl_pas * (1.0 - hg) + visg_pas * hg
            re = di * rhom * vme / vism if vism > 0 else 0.0
            ffm = self._friction_factor(re, ed)
            denom = c * (ffm / 4.0) ** 0.4
            if denom == 0.0:
                break
            vmc = ((0.725 + 4.15 * math.sqrt(hg)) / denom) ** 0.8333
            ratio = vmc / vme if vme > 0 else 1.0
            if 0.99 <= ratio <= 1.01:
                break
            vme = (vmc + vme) / 2.0
        vm = (vmc + vme) / 2.0
        vsl = vm * (1.0 - hgg)
        if hgg > 0.0:
            vsg = vm * hgg
        return vsl, vsg

    def _mpoint(self, di, ed, denl, deng, visl_pas, visg_pas, ang, surl):
        """
        Граничные точки переходов режима течения.

        :return: (vsgo, vsg1, vsl1, vsg2, vsl2, vsg3, vsl3). Type: tuple
        """
        alfa = 0.0174533 * ang
        dmin = 19.0 * math.sqrt((denl - deng) * surl / (denl**2 * 9.81))
        if ang > 70.0 and di > dmin * 0.95:
            vsl_tmp = 0.001
            vsgo = (
                vsl_tmp
                + 1.15
                * (9.81 * (denl - deng) * surl / denl**2) ** 0.25
                * math.sin(alfa)
            ) / 3.0
        else:
            vsgo = -1.0

        vsg3 = (
            3.1
            * (surl * 9.81 * math.sin(alfa) * (denl - deng)) ** 0.25
            / math.sqrt(deng)
        )

        vsg1, vsl1 = -1.0, -1.0
        if vsgo > 0.0:
            vsl1, vsg1 = self._dbtran(
                0.25, -1.0, di, ed, denl, deng, visl_pas, visg_pas, ang, surl
            )

        vsg2 = 0.2
        vsl2, vsg2 = self._dbtran(
            0.76, vsg2, di, ed, denl, deng, visl_pas, visg_pas, ang, surl
        )

        vsl3 = 0.0
        if vsg2 >= vsg3:
            vsg2 = vsg3
            vsl2, _ = self._dbtran(
                0.0, vsg2, di, ed, denl, deng, visl_pas, visg_pas, ang, surl
            )
            vsl3 = vsl2
            if vsg1 < vsg2:
                return vsgo, vsg1, vsl1, vsg2, vsl2, vsg3, vsl3
            vsg1 = vsg2
            return vsgo, vsg1, vsl1, vsg2, vsl2, vsg3, vsl3

        vsl3 = vsg3 / 0.76 - vsg3
        return vsgo, vsg1, vsl1, vsg2, vsl2, vsg3, vsl3

    def _fpup(self, vsl, vsg, di, ed, denl, deng, visl_pas, visg_pas, ang, surl):
        """
        Определить режим течения для восходящего наклонного/вертикального потока.

        :return: целочисленный код режима течения. Type: int
        """
        alfa = 0.0174533 * ang
        vsgo, vsg1, vsl1, vsg2, vsl2, vsg3, vsl3 = self._mpoint(
            di, ed, denl, deng, visl_pas, visg_pas, ang, surl
        )

        if vsg >= vsg3:
            return FlowPatternCode.ANNULAR.value

        if vsg <= vsg2:
            vslb, _ = self._dbtran(
                0.0, vsg, di, ed, denl, deng, visl_pas, visg_pas, ang, surl
            )
            if vsl < vslb:
                if vsgo > 0.0:
                    vsgb = (
                        vsl
                        + 1.15
                        * (9.81 * (denl - deng) * surl / denl**2) ** 0.25
                        * math.sin(alfa)
                    ) / 3.0
                    return (
                        FlowPatternCode.SLUG.value
                        if vsg > vsgb
                        else FlowPatternCode.BUBBLE.value
                    )
                else:
                    return FlowPatternCode.SLUG.value
            else:
                return FlowPatternCode.DISPERSED_BUBBLE.value
        else:
            vslb = vsg / 0.76 - vsg
            return (
                FlowPatternCode.DISPERSED_BUBBLE.value
                if vsl >= vslb
                else FlowPatternCode.SLUG.value
            )

    def _friction_factor(self, n_re: float, roughness_d: float) -> float:
        """
        Moody (Darcy-Weisbach) friction factor using Brkic explicit approximation.

        Laminar: f = 64/Re. Turbulent: Brkic (2011) approximation of Colebrook.

        :param n_re: Reynolds number. Type: float
        :param roughness_d: relative pipe roughness (eps/d). Type: float
        :return: Darcy friction factor. Type: float
        """
        if n_re == 0.0:
            return 0.0
        if n_re < 2000.0:
            return 64.0 / n_re
        # Brkic explicit approximation (case 3 in VBA)
        s = math.log(n_re / (1.816 * math.log(1.1 * n_re / math.log(1.0 + 1.1 * n_re))))
        f1 = -2.0 * math.log10(roughness_d / 3.71 + 2.0 * s / n_re)
        return 1.0 / f1**2
