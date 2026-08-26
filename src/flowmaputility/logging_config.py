"""
Настройка логирования утилиты.

Единая точка конфигурации: консольный обработчик показывает только
основные шаги пайплайна (INFO и выше), файловый обработчик с ротацией
пишет всё, включая построчную работу воркеров (DEBUG и выше).

Логи из дочерних процессов (multiprocessing.Pool) собираются через
общую очередь: воркеры кладут записи в очередь через QueueHandler,
а QueueListener в основном процессе разбирает их теми же двумя
обработчиками, что и логи основного процесса.
"""

import logging
import logging.handlers
import multiprocessing as mp

LOGGER_NAME = "flowmaputility"
LOG_FILE = "flowmaputility.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(processName)s] %(name)s: %(message)s"

MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 1

_configured = False
_queue: "mp.Queue | None" = None
_listener: logging.handlers.QueueListener | None = None


def setup_logging() -> "mp.Queue":
    """
    Настраивает логирование в основном процессе (идемпотентно —
    повторные вызовы возвращают уже созданную очередь без пересоздания
    обработчиков и слушателя).
    :return: Очередь, которую нужно передать воркерам для логирования.
    """
    global _configured, _queue, _listener

    if _configured:
        return _queue  # type: ignore

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    _queue = mp.Queue()
    _listener = logging.handlers.QueueListener(
        _queue, console_handler, file_handler, respect_handler_level=True
    )
    _listener.start()

    _configured = True
    return _queue


def configure_worker_logging(queue: "mp.Queue | None") -> None:
    """
    Настраивает логирование внутри дочернего процесса-воркера.
    Единственный обработчик — QueueHandler, кладущий записи в общую
    очередь на разбор в основном процессе.
    :param queue: Очередь логов, полученная из setup_logging().
        Если None — логирование в воркере не настраивается.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.handlers.clear()

    if queue is None:
        return

    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(logging.handlers.QueueHandler(queue))
