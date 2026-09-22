/**
 * Сверка AnsariModel/BeggsBrillModel с эталонными значениями, посчитанными
 * напрямую Python-реализацией (см. web/tests/fixtures/reference_values.json
 * и scratchpad/gen_reference.py, использованный для генерации).
 */

import { AnsariModel } from "../src/core/correlations/ansari.js";
import { BeggsBrillModel } from "../src/core/correlations/beggsBrill.js";
import { test, assertTrue } from "./tiny-test.js";

/** @type {any} */
let fixture = null;

async function loadFixture() {
  if (fixture) return fixture;
  const res = await fetch("./fixtures/reference_values.json");
  fixture = await res.json();
  return fixture;
}

function toPipe(p) {
  return { diameter: p.diameter, roughness: p.roughness, angle: p.angle };
}

function toFluid(f) {
  return {
    densityLiquid: f.density_liquid,
    densityGas: f.density_gas,
    viscosityLiquid: f.viscosity_liquid,
    viscosityGas: f.viscosity_gas,
    surfaceTension: f.surface_tension,
  };
}

function checkGroups(groups, ModelClass, label) {
  let checked = 0;
  const mismatches = [];
  for (const group of groups) {
    const model = new ModelClass(toPipe(group.pipe), toFluid(group.fluid));
    for (const c of group.cases) {
      const got = model.getPatternCode(c.vsl, c.vsg);
      checked++;
      if (got !== c.code) {
        mismatches.push(
          `${label} pipe=${JSON.stringify(group.pipe)} vsl=${c.vsl} vsg=${c.vsg}: ` +
            `ожидалось ${c.code}, получено ${got}`
        );
      }
    }
  }
  assertTrue(
    mismatches.length === 0,
    `${label}: ${mismatches.length} расхождений из ${checked}.\n` + mismatches.slice(0, 15).join("\n")
  );
}

test("AnsariModel: совпадает с эталонными значениями Python", async () => {
  const data = await loadFixture();
  checkGroups(data.ansari, AnsariModel, "Ansari");
});

test("BeggsBrillModel: совпадает с эталонными значениями Python", async () => {
  const data = await loadFixture();
  checkGroups(data.beggs_brill, BeggsBrillModel, "BeggsBrill");
});
