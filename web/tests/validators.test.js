import { validateFluidParams, validatePipeParams, validateSystemParams } from "../src/core/validators.js";
import { assertEqual, assertThrows, test } from "./tiny-test.js";

test("validators: validatePipeParams возвращает числовые поля", () => {
  const p = validatePipeParams(0.062, 0.00005, 90);
  assertEqual(p.diameter, 0.062);
  assertEqual(p.roughness, 0.00005);
  assertEqual(p.angle, 90);
});

test("validators: NaN бросает исключение", () => {
  assertThrows(() => validatePipeParams(NaN, 0.00005, 90));
});

test("validators: строка бросает исключение", () => {
  assertThrows(() => validatePipeParams(/** @type {any} */ ("0.062"), 0.00005, 90));
});

test("validators: boolean бросает исключение (как в Python isinstance(value, bool))", () => {
  assertThrows(() => validatePipeParams(/** @type {any} */ (true), 0.00005, 90));
});

test("validators: validateFluidParams проверяет все 5 полей", () => {
  const f = validateFluidParams(800, 50, 0.001, 0.00001, 0.01);
  assertEqual(f.densityLiquid, 800);
  assertEqual(f.surfaceTension, 0.01);
});

test("validators: validateSystemParams проверяет оба поля", () => {
  const s = validateSystemParams(101325, 293.15);
  assertEqual(s.pressure, 101325);
  assertEqual(s.temperature, 293.15);
});
