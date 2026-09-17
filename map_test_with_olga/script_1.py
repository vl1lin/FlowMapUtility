from pathlib import Path

import pandas as pd

from flowmaputility.builder import Builder

scenarios = pd.read_csv("flow_pattern_test_cases_2.csv")

SAVE_DIR = Path(
    r"C:\Users\79371\Desktop\проекты\FlowMapUtilite\map_test_with_olga\map_case\python\2"
)


def make_object(row: pd.Series) -> Builder:
    return (
        Builder()
        .set_pipe_params(
            float(row["diameter_m"]),  # type: ignore
            float(row["roughness_m"]),  # type: ignore
            float(row["angle_deg"]),  # type: ignore
        )
        .set_fluid_params(
            float(row["density_liquid_kgm3"]),  # type: ignore
            float(row["density_gas_kgm3"]),  # type: ignore
            float(row["viscosity_liquid_pas"]),  # type: ignore
            float(row["viscosity_gas_pas"]),  # type: ignore
            float(row["surface_tension_nm"]),  # type: ignore
        )
        .set_velocite_liquid(float(row["vsl_min_ms"]), float(row["vsl_max_ms"]))  # type: ignore
        .set_velocite_gas(float(row["vsg_min_ms"]), float(row["vsg_max_ms"]))  # type: ignore
        .set_model(str(row["model"]))
        .set_show_plot_flag(False)
        .set_scale_flag(True)
        .set_invert_axes(True)
        .set_save_path(str(SAVE_DIR / f"map_case_{row['case_id']}_invert.png"))
        .set_export_path(str(SAVE_DIR / f"map_case_{row['case_id']}_invert.csv"))
    )


def main() -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    for _, row in scenarios.iterrows():
        make_object(row).build_all().run()


if __name__ == "__main__":
    main()
