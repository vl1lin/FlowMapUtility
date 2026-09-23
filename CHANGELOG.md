# Changelog

## Unreleased

### Добавлено (Barnea)

- `BarneaModel` (`correlations/barnea.py`, ключ `"barnea"`, углы −90°…+90°): единая
  модель Barnea (1987) с расслоённым гладким и волновым, дисперсно-пузырьковым,
  кольцевым, пузырьковым и прерывистым режимами. Заглушка `BarneaModel` заменена
  полной реализацией; автовыбор по углу по-прежнему ведёт на ключ `"barnea"`, то есть
  теперь на работающую модель.
- `physics/stratified.py`: геометрия расслоённого течения, равновесный уровень
  жидкости, критерии Кельвина–Гельмгольца и Джеффриса. `physics/friction.py`:
  `fanning_friction_taitel_dukler` (скалярная и векторная версии).
- `FlowPatternCode.STRATIFIED_WAVY = 107` и `FlowPatternCode.CHURN = 108`, записи в
  палитре и подписях легенды карты.

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
