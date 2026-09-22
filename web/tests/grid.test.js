import { generateGrid } from "../src/core/grid.js";
import { assertClose, assertEqual, assertTrue, test } from "./tiny-test.js";

test("grid: logspace даёт ожидаемые эталонные точки (сверено вручную: 10^linspace(0,2,5))", () => {
  const grid = generateGrid([1, 100], [1, 100], 5, true);
  const expected = [1, 3.1622776601683795, 10, 31.622776601683796, 100];
  for (let i = 0; i < expected.length; i++) {
    assertClose(grid.vsl1d[i], expected[i], 1e-9, `vsl1d[${i}]:`);
  }
});

test("grid: linspace даёт равномерные точки от min до max включительно", () => {
  const grid = generateGrid([0, 10], [0, 10], 6, false);
  assertEqual(JSON.stringify(grid.vsl1d), JSON.stringify([0, 2, 4, 6, 8, 10]));
});

test("grid: resolution=1 возвращает единственную точку (min)", () => {
  const grid = generateGrid([2, 5], [2, 5], 1, false);
  assertEqual(JSON.stringify(grid.vsl1d), JSON.stringify([2]));
});

test("grid: log_scale автоматически отключается при min<=0", () => {
  const grid = generateGrid([0, 10], [1, 10], 5, true);
  assertEqual(grid.logScale, false);
});

test("grid: min>max в диапазоне переставляются местами", () => {
  const grid = generateGrid([10, 1], [1, 10], 5, false);
  assertEqual(grid.vsl1d[0], 1);
  assertEqual(grid.vsl1d[grid.vsl1d.length - 1], 10);
});

test("grid: vsl2d повторяет vsl1d по каждой строке", () => {
  const grid = generateGrid([1, 5], [1, 5], 4, false);
  for (const row of grid.vsl2d) {
    assertEqual(JSON.stringify(row), JSON.stringify(grid.vsl1d));
  }
});

test("grid: vsg2d - первая строка соответствует максимуму vsg, последняя - минимуму", () => {
  const grid = generateGrid([1, 5], [1, 100], 4, false);
  const maxVsg = grid.vsg1d[grid.vsg1d.length - 1];
  const minVsg = grid.vsg1d[0];
  assertEqual(grid.vsg2d[0][0], maxVsg);
  assertEqual(grid.vsg2d[grid.vsg2d.length - 1][0], minVsg);
  // константа по строке
  assertTrue(grid.vsg2d[0].every((v) => v === maxVsg));
});

test("grid: resolution и размеры матриц согласованы", () => {
  const grid = generateGrid([1, 5], [1, 5], 7, false);
  assertEqual(grid.resolution, 7);
  assertEqual(grid.vsl2d.length, 7);
  assertEqual(grid.vsl2d[0].length, 7);
  assertEqual(grid.vsg2d.length, 7);
  assertEqual(grid.vsg2d[0].length, 7);
});
