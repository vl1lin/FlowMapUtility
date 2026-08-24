import math

from flowmaputility.correlations.base import FlowPatternCode, IFlowModel
from flowmaputility.domain.params import FluidParams, PipeParams

_G = 9.81

_FP_SEG = 0
_FP_INT = 1
_FP_DIST = 2
_FP_TRANS = 3

_FLOW_PATTERN_MAP = {
    _FP_SEG: FlowPatternCode.STRATIFIED.value,
    _FP_TRANS: FlowPatternCode.SLUG.value,
    _FP_INT: FlowPatternCode.SLUG.value,
    _FP_DIST: FlowPatternCode.DISPERSED_BUBBLE.value,
}


class BeggsBrillModel(IFlowModel):
    """
    Модель Беггса-Брилла для расчета режима потока (угол от 0 до 75 не включительно).
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
        return "Beggs-Brill"

    @classmethod
    def angle_limit(cls) -> tuple[float, float]:
        """
        Метод класса, возвращает допустимый диапазон углов в градусах (min, max)
        """
        return (0.0, math.nextafter(75.0, -math.inf))

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
        vm = vsl + vsg
        lam_l = vsl / vm
        n_fr = vm**2 / (_G * diameter)

        fp = self._flow_pattern(lam_l, n_fr)
        return _FLOW_PATTERN_MAP[fp]

    def _flow_pattern(self, lam_l: float, n_fr: float) -> int:
        """
        Определение базового режима потока по карте Beggs-Brill.
        :param lam_l: безотрывное удержание жидкости (vsl / (vsl+vsg))
        :param n_fr: число Фруда смеси
        """
        if n_fr >= 316.0 * lam_l**0.302 or n_fr >= 0.5 * lam_l**-6.738:
            return _FP_DIST
        if n_fr <= 0.000925 * lam_l**-2.468:
            return _FP_SEG
        if n_fr <= 0.1 * lam_l**-1.452:
            return _FP_TRANS
        return _FP_INT
