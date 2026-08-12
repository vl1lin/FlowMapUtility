from Data_Block_1.adapter_for_data import PipeParamsAdapter, FluidParamsAdapter, SystemParamsAdapter
from Data_Block_1.data import PipeParams, FluidParams, SystemParams
from Grid_Generation.grid_generator import GridGenerator
from Grid_Generation.grid_info import GridInfo
from Correlation.model_abs import IFlowModel
from Correlation.fabric import ModelFabric
from Run_Core.process_manager import ProcessManager
from visualization.map import MapVisualizer
from functools import wraps
from collections.abc import Callable
from typing import TypeVar, Any

F = TypeVar("F", bound=Callable)

def requires(*attr: str):
    def decorator(method: F) -> F:
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            missing = [a for a in attr if getattr(self, a, None) is None]
            if missing:
                raise ValueError(
                    f"{method.__name__}: не заданы следующие атрибуты: "
                    f"{', '.join(missing)}\n"
                    "Вызови соответствующие et_*/build_* методы перед этим."
                )
            return method(self, *args, **kwargs)
        return wrapper #type: ignore
    return decorator



class Builder:
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
        self.correlation_fabric: ModelFabric | None = None
        self.model: IFlowModel | None = None
        # Блок 4
        self.n_count: int | None = None
        self.run_core: ProcessManager | None = None
        # Блок 5
        self.show_plot: bool = True
        self.save_path: str | None = None
        self.vis_manadger: MapVisualizer | None = None

    def set_pipe_params(self, diameter: float, roughness: float, angle: float) -> "Builder":
        pipe_params = PipeParamsAdapter(diameter, roughness, angle)
        self.pipe_params = pipe_params.to_si()
        return self

    def set_fluid_params(self,
        density_liquid: float,
        density_gas: float,
        viscosity_liquid: float,
        viscosity_gas: float,
        surface_tension: float) -> "Builder":
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
        system_params = SystemParamsAdapter(pressure, temperature)
        self.system_params = system_params.to_si()
        return self

    def set_velocite_liquid(self, velocity_min: float, velocity_max: float) -> "Builder":
        self.velocite_liquid = (velocity_min, velocity_max)
        return self

    def set_velocite_gas(self, velocity_min: float, velocity_max: float) -> "Builder":
        self.velocite_gas = (velocity_min, velocity_max)
        return self

    def set_resolution(self, resolution: int) -> "Builder":
        self.resolution = resolution
        return self

    def set_scale_flag(self, scale: bool = True) -> "Builder":
        self.scale_flag = scale
        return self

    def set_model(self, model: str) -> "Builder":
        self.model_name = model
        return self

    def set_count_of_workers(self, n_count: int) -> "Builder":
        self.n_count = n_count
        return self

    def set_show_plot_flag(self, show_plot: bool = True) -> "Builder":
        self.show_plot = show_plot
        return self

    def set_save_path(self, save_path: str) -> "Builder":
        self.save_path = save_path
        return self

    @requires("velocite_liquid", "velocite_gas")
    def build_grid_generator(self) -> "Builder":
        self.grid_generator = GridGenerator(
            self.velocite_liquid, # type:ignore
            self.velocite_gas, #type: ignore
            self.resolution,
            self.scale_flag,
        )
        return self

    @requires("grid_generator")
    def build_grid_info(self) -> "Builder":
        self.grid_info = self.grid_generator.generate() #type: ignore
        return self

    def build_model_fabric(self) -> "Builder":
        self.correlation_fabric = ModelFabric()
        return self

    @requires("correlation_fabric", "model_name")
    def build_model(self) -> "Builder":
        self.model = self.correlation_fabric.creat_model(self.model_name) #type: ignore
        return self

    @requires("model", "grid_info")
    def build_core(self) -> "Builder":
        self.run_core = ProcessManager(self.model, self.grid_info, self.n_count) #type: ignore
        return self

    @requires("grid_info")
    def build_visualization_manadger(self, code_matrix) -> "Builder":
        self.vis_manadger = MapVisualizer(code_matrix , self.grid_info, self.show_plot, self.save_path) #type: ignore
        return self

    def build_all(self) -> "Builder":
        self.build_grid_generator() \
            .build_grid_info() \
            .build_model_fabric() \
            .build_model() \
            .build_core()
        code_matrix = self.run_core.run() # type: ignore
        print(code_matrix)
        final_obj = self.build_visualization_manadger(code_matrix)
        return final_obj

    def run(self) -> None:
        self.vis_manadger.run() #type: ignore
