# Changelog

## Unreleased

### Добавлено (Mukherjee–Brill)

- Модель режимов `MukherjeeBrillModel` (`correlations/mukherjee_brill.py`, ключ фабрики
  `"mukherjee_brill"`, `name() == "Mukherjee-Brill"`) для углов от −90° до +90°:
  пузырьковый, пробковый, кольцевой и расслоённый режимы. Метод `classify()` возвращает
  диагностику (`MukherjeeBrillResult`). Автовыбор модели по углу не менялся: модель
  доступна только по явному ключу.

### Изменено

- Новая `AnsariModel` (`correlations/ansari.py`) с полными критериями перехода в
  кольцевой режим: Тёрнер (4.163) плюс критерии Barnea по перекрытию сечения плёнкой
  (4.165) и её устойчивости (4.169). Граница кольцевого режима теперь зависит от Vsl.
  Добавлены `AnsariSettings`, `AnsariResult`, `TransitionReason`, `FilmState` и метод
  `AnsariModel.classify()` для диагностики.
- Прежняя реализация переименована в `AnsariVBAModel` (`correlations/ansari_vba.py`,
  `name() == "Ansari-VBA"`), логика не менялась.
- Ключ `"ansari"` в `ModelFactory` теперь указывает на новую `AnsariModel`. Файлы
  кейсов с моделью `ansari` после обновления считаются новой моделью.

### Добавлено

- Ключ `"ansari_vba"` в `ModelFactory` для `AnsariVBAModel` (автовыбор по углу его
  не использует).
- Проверка `ModelFactory` на пересечение диапазонов углов автовыбора.
- `physics/friction.py` (`darcy_friction_factor`).
- Зависимость `scipy` (`scipy.optimize.brentq` для толщины плёнки).
