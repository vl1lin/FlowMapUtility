from Data_Block_1.adapter_for_data import PipeParamsAdapter, FluidParamsAdapter, SystemParamsAdapter
from Data_Block_1.data import PipeParams, FluidParams, SystemParams
from Grid_Generation.grid_generator import GridGenerator


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
        # Блок 3
        self.model: str | None = None
        # Блок 4
        self.n_count: int | None = None
        # Блок 5
        self.show_plot: bool = True
        self.save_path: str | None = None

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
        self.scale = scale
        return self

    def set_model(self, model: str) -> "Builder":
        self.model = model
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

    def build_grid_info(self) -> "Builder":
        if not self.velocite_liquid or not self.velocite_gas:
            raise ValueError("velocite_liquid and velocite_gas must be set")

        grid_generator = GridGenerator(
            self.velocite_liquid,
            self.velocite_gas,
            self.resolution,
            self.scale_flag,
        )
        self.grid_info = grid_generator.generate()
        return self

    def build_model_fabric(self) -> "Builder":

        return self
