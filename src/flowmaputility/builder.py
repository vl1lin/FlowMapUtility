"""
Основной объект для использования утилиты
"""

from collections.abc import Callable
from functools import wraps
from typing import TypeVar

from flowmaputility.correlations.base import IFlowModel
from flowmaputility.correlations.factory import ModelFactory
from flowmaputility.domain.adapters import (
    FluidParamsAdapter,
    PipeParamsAdapter,
    SystemParamsAdapter,
)
from flowmaputility.domain.params import FluidParams, PipeParams, SystemParams
from flowmaputility.engine.manager import ProcessManager
from flowmaputility.grid.generator import GridGenerator
from flowmaputility.grid.info import GridInfo
from flowmaputility.visualization.visualizer import MapVisualizer

F = TypeVar("F", bound=Callable)


def requires(*attr: str):
    """
    Декоратор, проверяющий наличие атрибутов перед вызовом метода.
    """

    def decorator(method: F) -> F:
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            missing = [a for a in attr if getattr(self, a, None) is None]
            if missing:
                raise ValueError(
                    f"{method.__name__}: не заданы следующие атрибуты: "
                    f"{', '.join(missing)}\n"
                    "Вызови соответствующие set_*/build_* методы перед этим."
                )
            return method(self, *args, **kwargs)

        return wrapper  # type: ignore

    return decorator


class Builder:
    """
    Основной класс через который можно строить карты режимов течения
    Данный класс основан на паттернах Строитель и Фасад.
    Перед вызовом запускающего метода необходимо настоить параметры
    Через методы set_*, далее вызвать метод build_all() или методы build_*
    После чего можно вызывать метод run()

    Attributes:
        pipe_params (PipeParams | None): Параметры трубы.
        fluid_params (FluidParams | None): Параметры жидкости.
        system_params (SystemParams | None): Параметры системы.
        velocite_liquid (tuple[float, float] | None):
            Минимальная и максимальная скорость жидкости.
        velocite_gas (tuple[float, float] | None):
            Минимальная и максимальная скорость газа.
        resolution (int): Разрешение сетки.
        scale_flag (bool): Флаг логорифмирования сетки. (Необязательный параметр.)
        grid_info (GridInfo | None): Информация о сетке.
        model_name (str | None): Название модели. (Необязательный параметр.)
        model (IFlowModel | None): Модель.
        n_count (int): Количество процессов. (Необязательный параметр.)
        show_plot (bool): Флаг отображения графика. (Необязательный параметр.)
        save_path (str | None): Путь для сохранения результата.(Необязательный параметр)
        vis_manadger (MapVisualizer | None): Визуализатор карты.
        run_core (ProcessManager | None): Менеджер процессов.
    """

    def __init__(self):
        # Блок 1
        self.pipe_params: PipeParams | None = None
        self.fluid_params: FluidParams | None = None
        self.system_params: SystemParams | None = None
        # Блок 2
        self.velocite_liquid: tuple[float, float] | None = None
        self.velocite_gas: tuple[float, float] | None = None
        self.resolution: int = 100
        self.scale_flag: bool = True
        self.grid_info: GridInfo | None = None
        self.grid_generator: GridGenerator | None = None
        # Блок 3
        self.model_name: str | None = None
        self.correlation_factory: ModelFactory | None = None
        self.model: IFlowModel | None = None
        # Блок 4
        self.n_count: int | None = None
        self.run_core: ProcessManager | None = None
        # Блок 5
        self.show_plot: bool = True
        self.save_path: str | None = None
        self.vis_manadger: MapVisualizer | None = None

    def set_pipe_params(
        self, diameter: float, roughness: float, angle: float
    ) -> "Builder":
        """
        Создает и устанавливает объект PipeParams.
        Также переводит параметры в систему СИ.
        :param diameter: диаметр сечения трубы: м, мм
        :param roughness: шероховатость трубы: м, мм
        :param angle: угол наклона трубы: градусы, радианы
        """
        pipe_params = PipeParamsAdapter(diameter, roughness, angle)
        self.pipe_params = pipe_params.to_si()
        return self

    def set_fluid_params(
        self,
        density_liquid: float,
        density_gas: float,
        viscosity_liquid: float,
        viscosity_gas: float,
        surface_tension: float,
    ) -> "Builder":
        """
        Создает и устанавливает объект FluidParams.
        Также переводит параметры в систему СИ.
        :param density_liquid: плотность жидкости: кг/м³, г/м³
        :param density_gas: плотность газа: кг/м³, г/м³
        :param viscosity_liquid: вязкость жидкости: Па·с, Н·с/м²
        :param viscosity_gas: вязкость газа: Па·с, Н·с/м²
        :param surface_tension: поверхностная плотность: Н/м, мПа
        """
        fluid_params = FluidParamsAdapter(
            density_liquid,
            density_gas,
            viscosity_liquid,
            viscosity_gas,
            surface_tension,
        )
        self.fluid_params = fluid_params.to_si()
        return self

    def set_system_params(self, pressure: float, temperature: float) -> "Builder":
        """
        Создает и устанавливает объект SystemParams.
        Также переводит параметры в систему СИ.
        :param pressure: давление: Па, атм
        :param temperature: температура: К, °C
        """
        system_params = SystemParamsAdapter(pressure, temperature)
        self.system_params = system_params.to_si()
        return self

    def set_velocite_liquid(
        self, velocity_min: float, velocity_max: float
    ) -> "Builder":
        """
        Устанавливает диапазон скорости жидкости (ось X).
        :param velocity_min: минимальная скорость: м/с
        :param velocity_max: максимальная скорость: м/с
        """
        self.velocite_liquid = (velocity_min, velocity_max)
        return self

    def set_velocite_gas(self, velocity_min: float, velocity_max: float) -> "Builder":
        """
        Устанавливает диапазон скорости газа (ось Y).
        :param velocity_min: минимальная скорость: м/с
        :param velocity_max: максимальная скорость: м/с
        """
        self.velocite_gas = (velocity_min, velocity_max)
        return self

    def set_resolution(self, resolution: int) -> "Builder":
        """
        Устанавливает разрешение сетки. (количество ячеек)
        Атрибут resolution является НЕОБЯЗАТЕЛЬНЫМ,
        ПО УМОЛЧАНИЮ равно 100.
        :param resolution: разрешение: количество ячеек
        """
        self.resolution = resolution
        return self

    def set_scale_flag(self, scale: bool = True) -> "Builder":
        """
        Устанавливает флаг логаримическкой шкалы.
        Атрибут scale_flag является НЕОБЯЗАТЕЛЬНЫМ,
        ПО УМОЛЧАНИЮ равно True.
        :param scale: флаг логаримической шкалы
        """
        self.scale_flag = scale
        return self

    def set_model(self, model: str) -> "Builder":
        """
        Устанавливает имя модели.
        Атрибут model_name является НЕОБЯЗАТЕЛЬНЫМ.
        ПО УМОЛЧАНИЮ равно None. Выбор модели будет происходить автоматически для угла.
        :param model: имя модели
        """
        self.model_name = model
        return self

    def set_count_of_workers(self, n_count: int) -> "Builder":
        """
        Устанавливает количество воркеров (количество процессов).
        Атрибут n_count является НЕОБЯЗАТЕЛЬНЫМ,
        ПО УМОЛЧАНИЮ равно количеству ядер процессора - 1.
        :param n_count: количество воркеров (процессов)
        """
        self.n_count = n_count
        return self

    def set_show_plot_flag(self, show_plot: bool = True) -> "Builder":
        """
        Устанавливает флаг отображения графика.
        Атрибут show_plot является НЕОБЯЗАТЕЛЬНЫМ,
        ПО УМОЛЧАНИЮ равно True.
        :param show_plot: флаг отображения графика
        """
        self.show_plot = show_plot
        return self

    def set_save_path(self, save_path: str) -> "Builder":
        """
        Устанавливает путь сохранения результатов.
        Атрибут save_path является НЕОБЯЗАТЕЛЬНЫМ.
        ПО УМОЛЧАНИЮ равно None.
        :param save_path: путь сохранения результатов
        """
        self.save_path = save_path
        return self

    @requires("velocite_liquid", "velocite_gas")
    def build_grid_generator(self) -> "Builder":
        """
        Создает и устанавливает объект генератора сетки.
        Перед вызовом этого метода нужно установить скорость жидкости и газа.
        :return: self
        """
        self.grid_generator = GridGenerator(
            self.velocite_liquid,  # type:ignore
            self.velocite_gas,  # type: ignore
            self.resolution,
            self.scale_flag,
        )
        return self

    @requires("grid_generator")
    def build_grid_info(self) -> "Builder":
        """
        Создает и устанавливает объект с информацией о сетке.
        Перед вызовом этого метода нужно создать генератор сетки.
        :return: self
        """
        self.grid_info = self.grid_generator.generate()  # type: ignore
        return self

    def build_model_factory(self) -> "Builder":
        """
        Создает и устанавливает объект фабрики моделей.
        :return: self
        """
        self.correlation_factory = ModelFactory()
        return self

    @requires("correlation_factory")
    def build_model(self) -> "Builder":
        """
        Создает и устанавливает модель.
        Перед вызовом этого метода нужно создать фабрику моделей
        :return: self
        """
        if not self.model_name:
            self.model = self.correlation_factory.creat_model(  # type: ignore
                self.pipe_params.angle,  # type: ignore
                self.pipe_params,  # type: ignore
                self.fluid_params,  # type: ignore
            )
        else:
            self.model = self.correlation_factory.creat_model(  # type: ignore
                self.model_name,  # type: ignore
                self.pipe_params,  # type: ignore
                self.fluid_params,  # type: ignore
            )
        return self

    @requires("model", "grid_info")
    def build_core(self) -> "Builder":
        """
        Создает и устанавливает ядро расчета.
        Перед вызовом этого метода нужно создать модель и информацию о сетке.
        :return: self
        """
        self.run_core = ProcessManager(self.model, self.grid_info, self.n_count)  # type: ignore
        return self

    @requires("grid_info")
    def build_visualization_manadger(self, code_matrix) -> "Builder":
        """
        Создает и устанавливает менеджер визуализации.
        Перед вызовом этого метода нужно создать информацию о сетке и
        передать матрицу кодов режимов.
        :param code_matrix: Матрица кодов режимов.
        :return: self
        """
        self.vis_manadger = MapVisualizer(
            code_matrix,
            self.grid_info,  # type: ignore
            self.model.name(),  # type: ignore
            self.show_plot,
            self.save_path,  # type: ignore
        )
        return self

    def build_all(self) -> "Builder":
        """
        Выполняет создание и установку всех компонентов:
            сетка, модель, ядро, менеджер визуализации.
        :return: self
        """
        self.build_grid_generator().build_grid_info().build_model_factory().build_model().build_core()
        code_matrix = self.run_core.run()  # type: ignore
        print(code_matrix)
        final_obj = self.build_visualization_manadger(code_matrix)
        return final_obj

    def run(self) -> None:
        """
        Запускает визуализацию.
        :return: None
        """
        self.vis_manadger.run()  # type: ignore
