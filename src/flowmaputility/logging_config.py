"""
Настройка логирования утилиты.

Единая точка конфигурации: консольный обработчик показывает только
основные шаги пайплайна (INFO и выше), файловый обработчик с ротацией
пишет всё, включая построчную работу воркеров (DEBUG и выше).

Логи из дочерних процессов (multiprocessing.Pool) собираются через
общую очередь: воркеры кладут записи в очередь через QueueHandler,
а QueueListener в основном процессе разбирает их теми же двумя
обработчиками, что и логи основного процесса.

QueueListener запускает собственный фоновый поток. Если этот поток уже
существует в момент os.fork() (создание пула процессов), дочерний
процесс может унаследовать внутренние блокировки логгера в захваченном
состоянии и зависнуть навсегда (см. предупреждение Python 3.12+ про
fork() в многопоточном процессе). Поэтому создание очереди/обработчиков
(setup_logging) и запуск потока-слушателя (start_queue_listener)
разделены: очередь и обработчики нужны уже на этапе создания пула
(они передаются воркерам), а сам поток должен стартовать только
ПОСЛЕ того, как пул воркеров уже создан (форк уже произошёл).
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
_listener_started = False
_queue: "mp.Queue | None" = None
_listener: logging.handlers.QueueListener | None = None


def setup_logging() -> "mp.Queue":
    """
    Настраивает обработчики и очередь логирования в основном процессе
    (идемпотентно — повторные вызовы возвращают уже созданную очередь
    без пересоздания обработчиков и слушателя).
    Поток-слушатель НЕ запускается — см. start_queue_listener().
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

    _configured = True
    return _queue


def start_queue_listener() -> None:
    """
    Запускает поток-слушатель очереди логов (идемпотентно).
    Вызывать нужно ПОСЛЕ создания mp.Pool — то есть после того, как
    дочерние процессы уже созданы через fork, чтобы не форкать процесс
    с лишним живым потоком (см. предупреждение Python 3.12+).
    """
    global _listener_started

    if _listener_started:
        return

    if _listener is None:
        raise RuntimeError("setup_logging() must be called before start_queue_listener()")

    _listener.start()
    _listener_started = True


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
