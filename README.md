# FlowMapUtility

Python-пакет для построения карт режимов многофазного потока в трубах
(модели Ansari и Beggs-Brill). Расчётное ядро (`src/flowmaputility/`) вызывается
через HTTP API (`src/flowmaputility/api/`) на FastAPI — backend для отдельного
frontend-репозитория.

## Локальный запуск API

```bash
pip install -e ".[dev]"
uvicorn flowmaputility.api.main:app --reload
```

Открыть `http://127.0.0.1:8000/docs` — интерактивная Swagger UI, там можно
отправить запрос к `/calculate` через форму, не собирая JSON руками.

Проверка через curl:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/models
curl -X POST http://127.0.0.1:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "pipe": {"diameter": 0.062, "roughness": 0.00005, "angle": 90},
    "fluid": {
      "density_liquid": 800, "density_gas": 50,
      "viscosity_liquid": 0.001, "viscosity_gas": 0.00001,
      "surface_tension": 0.01
    },
    "velocity_liquid": {"min": 0.1, "max": 0.5},
    "velocity_gas": {"min": 10, "max": 15},
    "resolution": 100
  }'
```

Все физические величины — в единицах СИ (метры, кг/м³, Па·с, Н/м, градусы).
`model` — необязательное поле (`"ansari"` или `"beggs_brill"`); если не
указать, модель выбирается автоматически по углу трубы.

## Тесты

```bash
pytest
```

## Переменные окружения

| Переменная | Назначение | По умолчанию |
|---|---|---|
| `FLOWMAP_API_ALLOWED_ORIGINS` | Список разрешённых CORS-origin'ов через запятую (домен frontend-репозитория). Пусто — ничего не разрешено. | `""` |
| `FLOWMAP_API_MAX_RESOLUTION` | Верхний предел `resolution` в `/calculate` — защита бесплатного хостинга от слишком тяжёлых расчётов. | `150` |

## Деплой на Render

В репозитории есть `render.yaml` — при создании Blueprint-сервиса на Render
он сам подставит Build/Start команды и имена переменных окружения.

- Build Command: `pip install .`
- Start Command: `uvicorn flowmaputility.api.main:app --host 0.0.0.0 --port $PORT`

После деплоя frontend-репозитория пропишите его домен в
`FLOWMAP_API_ALLOWED_ORIGINS` в настройках сервиса на Render и перезапустите
инстанс.

Бесплатный тариф Render "засыпает" при простое — первый запрос после паузы
будет медленным (холодный старт). Эндпоинт `/health` можно использовать для
внешнего пинга, который будет держать инстанс "разбуженным".
