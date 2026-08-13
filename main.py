from api.main_object import Builder


def main() -> None:
    obj = (
        Builder()
        .set_pipe_params(pipe_diameter_m, roughness_m, angle_deg)
        .set_fluid_params(rho_liq_si, rho_gas_si, mu_liq_si, mu_gas_si, sigma_si)
        .set_velocite_gas(0.1, 30)
        .set_velocite_liquid(0.1, 0.3)
        .set_resolution(100)
        .set_model("ansari")
    )

    obj.build_all().run()


if __name__ == "__main__":
    pipe_diameter_m = 0.062
    roughness_m = 0.0001
    angle_deg = 90.0

    rho_liq_si = 800.0
    rho_gas_si = 50.0
    # ВНИМАНИЕ: Переводим сПз -> Па*с здесь, до входа в модель
    mu_liq_si = 1.0 * 0.001
    mu_gas_si = 0.01 * 0.001
    sigma_si = 0.01
    main()
