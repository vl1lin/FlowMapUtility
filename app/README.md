# FlowMapUtility — JS/TS-порт (ветка `js`)

Статический сайт для расчёта карты режимов течения. Вся логика, которая в
Python-версии (`src/flowmaputility`) считалась на сервере (и опционально в
несколько процессов через `multiprocessing`), здесь портирована на чистый
JavaScript (ES-модули, без TypeScript-компилятора и без Node.js — см.
"Почему без сборки" ниже) и считается прямо в браузере, в один поток.

## Структура

```
web/
  index.html            статический сайт (форма + график)
  style.css
  src/
    core/                порт src/flowmaputility/* — чистая логика, без DOM
      patternCodes.js     correlations/base.py (FlowPatternCode) + visualization/palette.py
      validators.js       domain/validators.py + domain/params.py
      grid.js              grid/generator.py + grid/info.py
      engine.js             engine/manager.py + engine/worker.py (здесь — один поток вместо Pool)
      gridExporter.js        export/grid_exporter.py (Blob + скачивание вместо записи на диск)
      calculator.js           builder.py, упрощённый до одной функции calculate()
      correlations/
        base.js             correlations/base.py (класс FlowModel)
        ansari.js           correlations/ansari.py (построчный порт, включая итеративный _dbtran)
        beggsBrill.js        correlations/beggs_brill.py
        factory.js            correlations/factory.py
    ui/                   код, завязанный на DOM/Plotly (адаптировано из проекта FlowMapFrontend)
      form.js
      chart.js
      main.js
  tests/                 браузерный тестовый раннер (см. ниже)
```

## Как запустить сайт локально

Нужен любой статический HTTP-сервер (ES-модули не грузятся с `file://`
из-за CORS). Node.js не нужен — есть Python:

```bash
cd web
python -m http.server 8000
```

Открыть `http://127.0.0.1:8000/index.html`.

## Тесты

Node.js на машине разработки нет, поэтому вместо Vitest/Jest — минимальный
браузерный раннер (`tests/tiny-test.js` + `tests/test-runner.html`).
Корреляции (`AnsariModel`, `BeggsBrillModel`) сверяются с ~4900 эталонными
значениями, посчитанными напрямую Python-реализацией
(`tests/fixtures/reference_values.json`, см. скрипт генерации в истории
разработки) — так численный порт итеративного решателя Ансари проверен
построчно, а не только "на глаз".

```bash
cd web
python -m http.server 8000
```

Открыть `http://127.0.0.1:8000/tests/test-runner.html` — на странице и в
консоли будет `TEST_RESULT pass=N fail=0 total=N`.

Если на машине появится Node.js, тесты (за вычетом фреймворка) без
переделки переносятся в Vitest — модули написаны как обычные ES-модули без
браузерных зависимостей (кроме `gridExporter.js`, который трогает `document`
только в функциях скачивания, а не в тестируемой `buildCsvText`).

## Почему без сборки (TypeScript/Vite) и без multiprocessing

- На машине нет Node.js, а пользователь не хочет его ставить ради
  редких JS-задач — поэтому вместо TypeScript+Vite это обычный современный
  JavaScript (ES-модули) с JSDoc-аннотациями типов в комментариях (дают
  подсказки в редакторе без компиляции) и без шага сборки: `index.html`
  подключает `src/ui/main.js` напрямую через `<script type="module">`.
- Многопоточность (`multiprocessing.Pool` в `engine/manager.py`) заменена на
  простой последовательный цикл (`engine.js`) — в браузере нет
  `multiprocessing`, а сама точечная модель (Ansari/Beggs-Brill) достаточно
  лёгкая, чтобы посчитать сетку 100×100–300×300 за доли секунды в один поток.

## Контракт данных

`calculate()` из `core/calculator.js` по форме входа/выхода соответствует
контракту `POST /calculate` существующего FastAPI-backend
(`src/flowmaputility/api/*`, ветка `dev`) — том самом, под который уже
написан отдельный проект `FlowMapFrontend`. Совпадение не случайно: этот
контракт использовался как эталонная спецификация при портировании (backend
и `FlowMapFrontend` не трогались и продолжают работать как есть).
