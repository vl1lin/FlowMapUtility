import math

from flowmaputility.correlations.base import FlowPatternCode, IFlowModel
from flowmaputility.domain.params import FluidParams, PipeParams

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
        relative_roughness = self.pipe.roughness / diameter
        density_liquid = self.fluid.density_liquid
        density_gas = self.fluid.density_gas
        viscosity_liquid = self.fluid.viscosity_liquid
        viscosity_gas = self.fluid.viscosity_gas
        surface_tension = self.fluid.surface_tension

        pattern_code = self._fpup(
            vsl,
            vsg,
            diameter,
            relative_roughness,
            density_liquid,
            density_gas,
            viscosity_liquid,
            viscosity_gas,
            angle,
            surface_tension,
        )
        return pattern_code

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
