
from Grid_Generation.grid_info import GridInfo
from Grid_Generation.grid_generator import GridGenerator, GridGeneratorABS


class Grid:
    """
    Класс Grid управляет генерацией и выводом сетки.

    Attributes:
        grid_generator (GridGenerator): Объект генератора сетки.
        grid_printer: Функция вывода сетки.
    """
    def __init__(self, grid_generator: GridGenerator, grid_printer):
        self.grid_generator: GridGeneratorABS = grid_generator
        self.grid_printer = grid_printer

    def generate(self) -> GridInfo:
        grid_info = self.grid_generator.grid_generator()
        return grid_info
