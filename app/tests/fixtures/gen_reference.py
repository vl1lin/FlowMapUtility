"""
Генерирует web/tests/fixtures/reference_values.json - эталонные значения
кодов режима течения, посчитанные напрямую Python-реализацией
(src/flowmaputility). Используется браузерными тестами
web/tests/correlations.test.js и factory.test.js, чтобы сверить JS-порт
корреляций Ansari/Beggs-Brill (и выбор модели по углу) с оригиналом.

Запускать из корня репозитория:
    python web/tests/fixtures/gen_reference.py

Перегенерировать нужно, если меняется поведение
src/flowmaputility/correlations/* или factory.py.
"""

import itertools
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from flowmaputility.correlations.ansari import AnsariModel
from flowmaputility.correlations.beggs_brill import BeggsBrillModel
from flowmaputility.correlations.factory import ModelFactory
from flowmaputility.domain.params import FluidParams, PipeParams

vsl_values = [0.0, 1e-10, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 2.0, 3.0, 5.0, 10.0]
vsg_values = [0.0, 1e-10, 0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0, 50.0]

fluid_sets = [
    dict(density_liquid=800.0, density_gas=50.0, viscosity_liquid=0.001, viscosity_gas=0.00001, surface_tension=0.01),
    dict(density_liquid=1000.0, density_gas=1.2, viscosity_liquid=0.001, viscosity_gas=0.000018, surface_tension=0.072),
    dict(density_liquid=850.0, density_gas=20.0, viscosity_liquid=0.005, viscosity_gas=0.000015, surface_tension=0.03),
]

pipe_sets_ansari = [
    dict(diameter=0.062, roughness=0.00005, angle=90.0),
    dict(diameter=0.1, roughness=0.0001, angle=75.0),
    dict(diameter=0.05, roughness=0.0000, angle=80.0),
]

pipe_sets_bb = [
    dict(diameter=0.062, roughness=0.00005, angle=0.0),
    dict(diameter=0.1, roughness=0.0001, angle=45.0),
    dict(diameter=0.05, roughness=0.0, angle=74.9),
]

results = {"ansari": [], "beggs_brill": []}

for pipe_kwargs, fluid_kwargs in itertools.product(pipe_sets_ansari, fluid_sets):
    pipe = PipeParams(**pipe_kwargs)
    fluid = FluidParams(**fluid_kwargs)
    model = AnsariModel(pipe, fluid)
    cases = []
    for vsl, vsg in itertools.product(vsl_values, vsg_values):
        code = model.get_pattern_code(vsl, vsg)
        cases.append({"vsl": vsl, "vsg": vsg, "code": code})
    results["ansari"].append({"pipe": pipe_kwargs, "fluid": fluid_kwargs, "cases": cases})

for pipe_kwargs, fluid_kwargs in itertools.product(pipe_sets_bb, fluid_sets):
    pipe = PipeParams(**pipe_kwargs)
    fluid = FluidParams(**fluid_kwargs)
    model = BeggsBrillModel(pipe, fluid)
    cases = []
    for vsl, vsg in itertools.product(vsl_values, vsg_values):
        code = model.get_pattern_code(vsl, vsg)
        cases.append({"vsl": vsl, "vsg": vsg, "code": code})
    results["beggs_brill"].append({"pipe": pipe_kwargs, "fluid": fluid_kwargs, "cases": cases})

# Выбор модели по углу (ModelFactory.creat_model(angle, ...))
factory = ModelFactory()
angle_selection = []
for angle in [0.0, 10.0, 45.0, 74.0, 74.9999, 75.0, 76.0, 80.0, 90.0]:
    pipe = PipeParams(diameter=0.062, roughness=0.00005, angle=angle)
    fluid = FluidParams(**fluid_sets[0])
    model = factory.creat_model(angle, pipe, fluid)
    angle_selection.append({"angle": angle, "model": model.name()})
results["angle_selection"] = angle_selection

out_path = Path(__file__).with_name("reference_values.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(
    f"wrote {out_path};",
    "ansari cases:", sum(len(g["cases"]) for g in results["ansari"]),
    "beggs_brill cases:", sum(len(g["cases"]) for g in results["beggs_brill"]),
)
