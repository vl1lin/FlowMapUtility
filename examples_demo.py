"""
Демонстрационные примеры использования FlowMapUtility.

Отдельный скрипт (не ноутбук examples.ipynb) — показывает актуальную
версию API: Builder, автоматический выбор корреляции по углу трубы
(Ansari для 75-90 градусов, Beggs-Brill для 0-75), явный выбор модели,
логирование (по умолчанию библиотека молчит, вывод включается явно
через configure_default_logging()) и опциональный прогресс-бар расчета.

Все параметры трубы и флюида передаются сразу в СИ (метры, Па*с,
кг/м3, градусы) — валидаторы больше не гадают единицы измерения,
поэтому переводить их нужно самостоятельно, до вызова set_*.
"""

from pathlib import Path

from flowmaputility.builder import Builder
from flowmaputility.logging_config import configure_default_logging

OUTPUT_DIR = Path("demo_output")


def example_library_silent_by_default() -> None:
    """
    Пример 0: без единого вызова configure_default_logging() библиотека
    не пишет ничего — ни в консоль, ни в файл. Так и должна вести себя
    библиотека, встроенная в чужое приложение (см. logging_config.py).
    """
    print("\n=== Пример 0: библиотека молчит по умолчанию (без логов) ===")

    obj = (
        Builder()
        .set_pipe_params(0.062, 0.0001, 90.0)
        .set_fluid_params(800.0, 50.0, 0.001, 0.00001, 0.01)
        .set_velocite_liquid(0.1, 0.3)
        .set_velocite_gas(0.1, 30)
        .set_resolution(50)
        .set_show_plot_flag(False)
    )
    obj.build_all()
    print("Готово — выше не должно быть ни одной строчки от flowmaputility.")


def example_vertical_pipe() -> None:
    """
    Пример 1: вертикальная труба (90 градусов) — автоматически
    выбирается модель Ансари (валидна для 75-90 градусов).
    """
    print("\n=== Пример 1: вертикальная труба, 90 градусов, модель Ansari (автовыбор) ===")

    pipe_diameter_m = 0.062
    roughness_m = 0.0001
    angle_deg = 90.0

    density_liquid_si = 800.0
    density_gas_si = 50.0
    viscosity_liquid_si = 1.0 * 0.001  # 1 сПз -> Па*с
    viscosity_gas_si = 0.01 * 0.001  # 0.01 сПз -> Па*с
    surface_tension_si = 0.01

    obj = (
        Builder()
        .set_pipe_params(pipe_diameter_m, roughness_m, angle_deg)
        .set_fluid_params(
            density_liquid_si,
            density_gas_si,
            viscosity_liquid_si,
            viscosity_gas_si,
            surface_tension_si,
        )
        .set_velocite_liquid(0.1, 0.3)
        .set_velocite_gas(0.1, 30)
        .set_resolution(100)
        .set_save_path(str(OUTPUT_DIR / "example_1_vertical_ansari.png"))
    )
    obj.build_all().run()


def example_horizontal_inclined_pipe() -> None:
    """
    Пример 2: наклонная труба (30 градусов от горизонтали) —
    автоматически выбирается модель Beggs-Brill (валидна для
    углов от 0 до 75 градусов, не включая 75).
    """
    print(
        "\n=== Пример 2: наклонная труба, 30 градусов, модель Beggs-Brill (автовыбор) ==="
    )

    obj = (
        Builder()
        .set_pipe_params(0.062, 0.0001, 30.0)
        .set_fluid_params(800.0, 50.0, 1.0 * 0.001, 0.01 * 0.001, 0.01)
        .set_velocite_liquid(0.1, 0.3)
        .set_velocite_gas(0.1, 30)
        .set_resolution(100)
        .set_save_path(str(OUTPUT_DIR / "example_2_inclined_beggs_brill.png"))
    )
    obj.build_all().run()


def example_explicit_model_selection() -> None:
    """
    Пример 3: явный выбор модели через set_model() вместо автовыбора
    по углу. Имя модели регистронезависимо, дефис/пробел неважны
    ("Beggs-Brill" == "beggs_brill" == "BEGGS BRILL").
    """
    print("\n=== Пример 3: явный выбор модели через set_model('Beggs-Brill') ===")

    obj = (
        Builder()
        .set_pipe_params(0.062, 0.0001, 45.0)
        .set_fluid_params(800.0, 50.0, 1.0 * 0.001, 0.01 * 0.001, 0.01)
        .set_velocite_liquid(0.1, 0.3)
        .set_velocite_gas(0.1, 30)
        .set_resolution(100)
        .set_model("Beggs-Brill")
        .set_save_path(str(OUTPUT_DIR / "example_3_explicit_model.png"))
    )
    obj.build_all().run()


def example_progress_bar() -> None:
    """
    Пример 4: прогресс-бар расчета на сетке покрупнее. Выключен по
    умолчанию (см. Builder.show_progress) — включается явно.
    """
    print("\n=== Пример 4: прогресс-бар расчета (set_show_progress) ===")

    obj = (
        Builder()
        .set_pipe_params(0.062, 0.0001, 90.0)
        .set_fluid_params(800.0, 50.0, 1.0 * 0.001, 0.01 * 0.001, 0.01)
        .set_velocite_liquid(0.1, 0.3)
        .set_velocite_gas(0.1, 30)
        .set_resolution(200)
        .set_show_progress(True)
        .set_save_path(str(OUTPUT_DIR / "example_4_progress_bar.png"))
    )
    obj.build_all().run()


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Демонстрируем поведение "по умолчанию" ДО включения логирования.
    example_library_silent_by_default()

    # Дальше — осознанный opt-in: мы тут выступаем приложением, а не
    # библиотекой внутри чужого кода, поэтому включаем готовую
    # конфигурацию логирования (консоль=основные шаги, файл=всё).
    configure_default_logging()

    example_vertical_pipe()
    example_horizontal_inclined_pipe()
    example_explicit_model_selection()
    example_progress_bar()

    print(f"\nВсе примеры выполнены. Графики сохранены в {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
