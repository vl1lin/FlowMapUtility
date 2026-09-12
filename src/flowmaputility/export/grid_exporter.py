import csv
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

import numpy as np

if TYPE_CHECKING:
    from flowmaputility.grid.info import GridInfo


class GridExporter:
    """
    Экспортирует рассчитанную сетку (скорости газа/жидкости и коды режимов)
    в CSV или XLSX.
    :param grid: Информация о сетке (объект GridInfo)
    :param codes: Матрица кодов режимов
    """

    HEADERS = ("Скорость газа, м/с", "Код режима", "Скорость жидкости, м/с")

    def __init__(self, grid: "GridInfo", codes: np.ndarray) -> None:
        self.grid = grid
        self.codes = codes

    def export(self, path: str) -> None:
        """
        Экспортирует сетку в файл. Формат определяется по расширению пути.
        :param path: Путь до файла (.csv или .xlsx)
        """
        suffix = Path(path).suffix.lower()
        if suffix == ".csv":
            self._to_csv(path)
        elif suffix in (".xlsx", ".xls"):
            self._to_excel(path)
        else:
            raise ValueError(f"Неподдерживаемое расширение файла: {suffix!r}")

    def _rows(self) -> Iterator[tuple[float, int, float]]:
        """
        Возвращает построчно (скорость газа, код режима, скорость жидкости),
        разворачивая 2D-сетку в длинный формат.
        """
        vsg_flat = self.grid.vsg_2d.ravel()
        codes_flat = self.codes.ravel()
        vsl_flat = self.grid.vsl_2d.ravel()
        for vsg, code, vsl in zip(vsg_flat, codes_flat, vsl_flat):
            yield float(vsg), int(code), float(vsl)

    def _to_csv(self, path: str) -> None:
        """
        Сохраняет сетку в CSV (без внешних зависимостей).
        :param path: Путь до .csv файла
        """
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(self.HEADERS)
            writer.writerows(self._rows())

    def _to_excel(self, path: str) -> None:
        """
        Сохраняет сетку в XLSX через openpyxl (опциональная зависимость).
        :param path: Путь до .xlsx файла
        """
        try:
            from openpyxl import Workbook
        except ImportError as e:
            e.add_note(
                "Для экспорта в xlsx нужен пакет openpyxl: "
                "pip install openpyxl (или flowmaputility[excel])"
            )
            raise

        wb = Workbook()
        ws = wb.active
        ws.append(self.HEADERS)  # type: ignore
        for row in self._rows():
            ws.append(row)  # type: ignore
        wb.save(path)
