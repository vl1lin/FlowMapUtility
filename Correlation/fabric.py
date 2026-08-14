from typing import overload

from Correlation.ansari import AnsariModel
from Correlation.model_abs import IFlowModel
from Data_Block_1.data import FluidParams, PipeParams


class ModelFabric:
    """
    Фабрика для создания моделей расчета режима потока
    Основной элемент: словарь MODELS (название модели -> класс модели)
    """

    def __init__(self):
        self.MODELS: dict[str, type[IFlowModel]] = {
            "ansari": AnsariModel,
        }

    @overload
    def creat_model(
        self, model_name_or_angel: str, pipe: PipeParams, fluid: FluidParams
    ) -> IFlowModel:
        pass

    @overload
    def creat_model(
        self, model_name_or_angel: float, pipe: PipeParams, fluid: FluidParams
    ) -> IFlowModel:
        pass

    def creat_model(
        self, model_name_or_angel: str | float, pipe: PipeParams, fluid: FluidParams
    ) -> IFlowModel:
        """
        Создает модель расчета режима потока по имени или углу
        :param model_name_or_angel: Имя модели или угол в градусах
        :param pipe: Объект PipeParams, в котором информация о трубе
        :param fluid: Объект FluidParams,
        в котором информация о свойствах флюидов в потоке
        :return: Объект модели расчета режима потока (наследник IFlowModel)
        """
        if isinstance(model_name_or_angel, str):
            try:
                model = self.MODELS[self.parse_name(model_name_or_angel)](pipe, fluid)
                model.validate_angle()
                return model
            except KeyError:
                raise ValueError(f"Model {model_name_or_angel} is not supported")
        elif isinstance(model_name_or_angel, float):
            for model in self.MODELS.values():
                angle_range = model.angle_limit()
                if angle_range[0] <= model_name_or_angel <= angle_range[1]:
                    return model(pipe, fluid)
            raise ValueError(
                f"Angle {model_name_or_angel} is out of range for any model"
            )
        else:
            raise TypeError(f"Expected str or float, got {type(model_name_or_angel)}")

    def parse_name(self, model_name: str) -> str:
        """
        Приводит имя модели к нижнему регистру и
        заменяет пробелы и дефисы на подчеркивания
        (единый стиль именования моделей в словере MODELS)
        :param model_name: Имя модели
        :return: Приведённое к нижнему регистру имя модели
        """
        model_name_lower = model_name.lower().replace("-", "_").replace(" ", "_")
        return model_name_lower
