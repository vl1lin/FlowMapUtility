import { buildCsvText } from "../src/core/gridExporter.js";
import { generateGrid } from "../src/core/grid.js";
import { assertEqual, assertTrue, test } from "./tiny-test.js";

test("gridExporter: CSV содержит BOM, заголовок и строки в порядке (vsg, code, vsl)", () => {
  const grid = generateGrid([1, 2], [10, 20], 2, false);
  // resolution=2 -> vsl1d=[1,2], vsg1d=[10,20]; vsg2d развёрнут: строка0=20, строка1=10
  const codes = [
    [100, 101],
    [102, 103],
  ];
  const csv = buildCsvText(grid, codes);

  assertTrue(csv.startsWith("﻿"), "должен начинаться с BOM");
  const lines = csv.replace(/^﻿/, "").trim().split("\r\n");
  // поля с запятыми должны экранироваться кавычками, как у Python csv.writer
  assertEqual(lines[0], '"Скорость газа, м/с",Код режима,"Скорость жидкости, м/с"');
  // строка i=0,j=0: vsg2d[0][0]=20, codes[0][0]=100, vsl2d[0][0]=1
  assertEqual(lines[1], "20,100,1");
  // строка i=0,j=1: vsg2d[0][1]=20, codes[0][1]=101, vsl2d[0][1]=2
  assertEqual(lines[2], "20,101,2");
  // строка i=1,j=0: vsg2d[1][0]=10, codes[1][0]=102, vsl2d[1][0]=1
  assertEqual(lines[3], "10,102,1");
  assertEqual(lines[4], "10,103,2");
  assertEqual(lines.length, 5);
});
