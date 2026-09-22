import { calculate } from "../src/core/calculator.js";
import { assertEqual, assertTrue, test } from "./tiny-test.js";

const baseParams = () => ({
  pipe: { diameter: 0.062, roughness: 0.00005, angle: 90 },
  fluid: {
    densityLiquid: 800,
    densityGas: 50,
    viscosityLiquid: 0.001,
    viscosityGas: 0.00001,
    surfaceTension: 0.01,
  },
  velocityLiquid: { min: 0.1, max: 0.5 },
  velocityGas: { min: 10, max: 15 },
  resolution: 5,
  logScale: true,
});

test("calculator: сквозной расчёт возвращает согласованную форму данных (как ответ POST /calculate)", () => {
  const result = calculate(baseParams());
  assertEqual(result.modelName, "Ansari");
  assertEqual(result.grid.resolution, 5);
  assertEqual(result.codeMatrix.length, 5);
  assertEqual(result.codeMatrix[0].length, 5);
  assertTrue(Object.prototype.hasOwnProperty.call(result.patternLegend, 100));
});

test("calculator: model=null выбирает модель автоматически по углу трубы", () => {
  const params = baseParams();
  params.pipe.angle = 30;
  params.model = null;
  const result = calculate(params);
  assertEqual(result.modelName, "Beggs-Brill");
});

test("calculator: model задаёт модель явно", () => {
  const params = baseParams();
  params.model = "beggs_brill";
  params.pipe.angle = 10;
  const result = calculate(params);
  assertEqual(result.modelName, "Beggs-Brill");
});
