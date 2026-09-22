import { AnsariModel } from "../src/core/correlations/ansari.js";
import { BeggsBrillModel } from "../src/core/correlations/beggsBrill.js";
import { availableModels, createModel, parseModelName } from "../src/core/correlations/factory.js";
import { assertEqual, assertThrows, assertTrue, test } from "./tiny-test.js";

const pipe = { diameter: 0.062, roughness: 0.00005, angle: 90.0 };
const fluid = {
  densityLiquid: 800,
  densityGas: 50,
  viscosityLiquid: 0.001,
  viscosityGas: 0.00001,
  surfaceTension: 0.01,
};

test("factory: availableModels возвращает отсортированный список", () => {
  assertEqual(JSON.stringify(availableModels()), JSON.stringify(["ansari", "beggs_brill"]));
});

test("factory: parseModelName нормализует регистр/дефисы/пробелы", () => {
  assertEqual(parseModelName("Beggs-Brill"), "beggs_brill");
  assertEqual(parseModelName("beggs brill"), "beggs_brill");
  assertEqual(parseModelName("ANSARI"), "ansari");
});

test("factory: создание модели по имени", () => {
  const model = createModel("ansari", pipe, fluid);
  assertTrue(model instanceof AnsariModel);
});

test("factory: неизвестное имя модели бросает исключение", () => {
  assertThrows(() => createModel("unknown_model", pipe, fluid));
});

test("factory: создание модели по имени с недопустимым для неё углом бросает исключение", () => {
  assertThrows(() => createModel("ansari", { ...pipe, angle: 10 }, fluid));
});

test("factory: угол вне диапазона всех моделей бросает исключение", () => {
  assertThrows(() => createModel(200, pipe, fluid));
});

test("factory: выбор модели по углу совпадает с эталоном Python", async () => {
  const res = await fetch("./fixtures/reference_values.json");
  const data = await res.json();
  for (const { angle, model: expectedName } of data.angle_selection) {
    const model = createModel(angle, { ...pipe, angle }, fluid);
    assertEqual(
      /** @type {any} */ (model.constructor).modelName,
      expectedName,
      `angle=${angle}:`
    );
  }
});

test("factory: model=null выбирает модель по углу трубы (как Builder.build_model)", () => {
  const model = createModel(null, pipe, fluid);
  assertTrue(model instanceof AnsariModel);
  const modelHorizontal = createModel(null, { ...pipe, angle: 10 }, fluid);
  assertTrue(modelHorizontal instanceof BeggsBrillModel);
});
