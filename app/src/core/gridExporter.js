/**
 * Экспорт рассчитанной сетки (скорости газа/жидкости и коды режимов) в CSV/XLSX.
 * Порт src/flowmaputility/export/grid_exporter.py: там писали файл на диск,
 * здесь - собираем Blob и отдаём браузеру на скачивание.
 *
 * Экспорт в XLSX требует библиотеку SheetJS (глобальный объект `XLSX`),
 * подключаемую в index.html через CDN - см. README.
 */

const HEADERS = ["Скорость газа, м/с", "Код режима", "Скорость жидкости, м/с"];

/**
 * Экранирует поле CSV аналогично Python csv.writer (quoting=QUOTE_MINIMAL по
 * умолчанию): значение оборачивается в кавычки, если содержит запятую,
 * кавычку или перевод строки; внутренние кавычки удваиваются.
 * @param {string | number} value
 * @returns {string}
 */
function csvField(value) {
  const str = String(value);
  if (/[",\r\n]/.test(str)) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

/**
 * @param {import("./grid.js").GridInfo} grid
 * @param {number[][]} codes
 * @returns {Array<[number, number, number]>} построчно (vsg, code, vsl),
 *   разворачивая 2D-сетку в длинный формат (порядок как у numpy .ravel(): по строкам).
 */
function toRows(grid, codes) {
  const rows = [];
  for (let i = 0; i < grid.resolution; i++) {
    for (let j = 0; j < grid.resolution; j++) {
      rows.push([grid.vsg2d[i][j], codes[i][j], grid.vsl2d[i][j]]);
    }
  }
  return rows;
}

/**
 * @param {string} filename
 * @param {Blob} blob
 */
function downloadBlob(filename, blob) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Строит текст CSV (с BOM, аналог encoding="utf-8-sig" в Python-версии, чтобы
 * Excel корректно определял кодировку и кириллицу в заголовках). Вынесено
 * отдельно от exportToCsv, чтобы быть тестируемой чистой функцией (без DOM).
 * @param {import("./grid.js").GridInfo} grid
 * @param {number[][]} codes
 * @returns {string}
 */
export function buildCsvText(grid, codes) {
  const rows = toRows(grid, codes);
  const lines = [
    HEADERS.map(csvField).join(","),
    ...rows.map((r) => r.map(csvField).join(",")),
  ];
  return "﻿" + lines.join("\r\n") + "\r\n";
}

/**
 * Экспортирует сетку в CSV и запускает скачивание файла.
 * @param {import("./grid.js").GridInfo} grid
 * @param {number[][]} codes
 * @param {string} [filename]
 */
export function exportToCsv(grid, codes, filename = "flow_map.csv") {
  const csvText = buildCsvText(grid, codes);
  downloadBlob(filename, new Blob([csvText], { type: "text/csv;charset=utf-8" }));
}

/**
 * Экспортирует сетку в XLSX (через глобальный SheetJS `XLSX`) и запускает скачивание.
 * @param {import("./grid.js").GridInfo} grid
 * @param {number[][]} codes
 * @param {string} [filename]
 */
export function exportToXlsx(grid, codes, filename = "flow_map.xlsx") {
  if (typeof XLSX === "undefined") {
    throw new Error(
      "Для экспорта в XLSX нужна библиотека SheetJS - подключите её в index.html"
    );
  }
  const rows = toRows(grid, codes);
  const sheetData = [HEADERS, ...rows];
  const worksheet = XLSX.utils.aoa_to_sheet(sheetData);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Sheet1");
  XLSX.writeFile(workbook, filename);
}

/**
 * Экспортирует сетку в файл, формат определяется по расширению.
 * @param {import("./grid.js").GridInfo} grid
 * @param {number[][]} codes
 * @param {string} filename путь/имя файла (.csv или .xlsx)
 */
export function exportGrid(grid, codes, filename) {
  const suffix = filename.slice(filename.lastIndexOf(".")).toLowerCase();
  if (suffix === ".csv") {
    exportToCsv(grid, codes, filename);
  } else if (suffix === ".xlsx" || suffix === ".xls") {
    exportToXlsx(grid, codes, filename);
  } else {
    throw new Error(`Неподдерживаемое расширение файла: ${suffix}`);
  }
}
