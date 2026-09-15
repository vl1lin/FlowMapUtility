from flowmaputility.correlations.base import IFlowModel


class BarneaModel(IFlowModel):
    @classmethod
    def name(cls) -> str:
        """
        Метод класса, возвращает имя модели
        """
        return "Barnea"

    @classmethod
    def angle_limit(cls) -> tuple[float, float]:
        """
        Метод класса, возвращает допустимый диапазон углов в градусах (min, max)
        """
        return (0.0, 90.0)
