"""
Логирование FlowMapUtility как библиотеки.

По умолчанию пакет НИКАК не настраивает вывод логов — на верхний
логгер "flowmaputility" повешен только NullHandler (стандартная
рекомендация для библиотек: https://docs.python.org/3/howto/logging.html#library-config).
Если приложение, использующее эту библиотеку, само настроило
логирование (basicConfig/dictConfig на root, либо конкретно на
"flowmaputility") — наши записи попадут туда естественным образом,
через штатный propagate. Если ничего не настроено — записи молча
гасятся NullHandler'ом, никакого вывода в файл/консоль без спроса.

configure_default_logging() — готовая конфигурация (консоль=только
INFO и выше, ротируемый файл=всё от DEBUG) для тех, кто хочет её
использовать. Она НЕ вызывается автоматически нигде внутри пакета —
это осознанный выбор вызывающего кода (см. main.py).

Отдельная сложность — воркеры multiprocessing.Pool: они не могут
писать напрямую в обработчики главного процесса. Поэтому лог-записи
из воркеров идут через общую очередь и в главном процессе
"дописываются" через реальный логгер "flowmaputility"
(logger.handle(record)) — то есть ведут себя так, как будто вызов
logger.debug(...) произошёл прямо в главном процессе, подчиняясь
ровно тем обработчикам/уровням, которые (если) настроило приложение.
"""

import logging
import logging.handlers
import multiprocessing as mp

LOGGER_NAME = "flowmaputility"
LOG_FILE = "flowmaputility.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(processName)s] %(name)s: %(message)s"

MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 1

if not any(
    isinstance(h, logging.NullHandler) for h in logging.getLogger(LOGGER_NAME).handlers
):
    logging.getLogger(LOGGER_NAME).addHandler(logging.NullHandler())

_default_logging_configured = False

_queue: "mp.Queue | None" = None
_listener: "logging.handlers.QueueListener | None" = None
_listener_started = False


class _RoutingQueueListener(logging.handlers.QueueListener):
    """
    QueueListener, диспетчеризующий записи через реальный логгер по
    его имени (record.name), а не через фиксированный список
    обработчиков. Так запись из воркера подчиняется той конфигурации
    логирования, которую (если) настроило приложение в главном
    процессе — а не той, что решила бы сама библиотека.
    """

    def handle(self, record: logging.LogRecord) -> None:
        record = self.prepare(record)
        logger = logging.getLogger(record.name)
        # Logger.handle() сам по себе НЕ проверяет эффективный уровень
        # логгера (это делают удобные методы вроде .debug()/.info() —
        # но у нас тут уже готовый record, а не такой вызов). Воркер
        # шлёт в очередь вообще всё, от DEBUG и выше, безусловно —
        # именно тут, на стороне главного процесса, должна применяться
        # реальная настройка уровня (наша через configure_default_logging
        # или сделанная самим приложением), иначе DEBUG из воркеров
        # пролезал бы мимо уровня, который выставило приложение.
        if logger.isEnabledFor(record.levelno):
            logger.handle(record)


def get_log_queue() -> "mp.Queue":
    """
    Возвращает очередь для передачи лог-записей из воркеров в главный
    процесс (идемпотентно — создаётся один раз за всё время жизни
    процесса). Не трогает конфигурацию логгера "flowmaputility" и не
    производит никакого вывода — только служебная инфраструктура для
    мультипроцессности.
    :return: Очередь, которую нужно передать воркерам через init_worker.
    """
    global _queue, _listener

    if _queue is not None:
        return _queue

    _queue = mp.Queue()
    _listener = _RoutingQueueListener(_queue)
    return _queue


def start_queue_listener() -> None:
    """
    Запускает поток-слушатель очереди логов (идемпотентно).
    Вызывать нужно ПОСЛЕ создания mp.Pool — то есть после того, как
    дочерние процессы уже созданы через fork, чтобы не форкать процесс
    с лишним живым потоком (см. предупреждение Python 3.12+ про
    fork() в многопоточном процессе).
    """
    global _listener_started

    if _listener_started:
        return

    if _listener is None:
        raise RuntimeError("get_log_queue() must be called before start_queue_listener()")

    _listener.start()
    _listener_started = True


def configure_worker_logging(queue: "mp.Queue | None") -> None:
    """
    Настраивает логирование внутри дочернего процесса-воркера.
    Единственный обработчик — QueueHandler, кладущий записи в общую
    очередь на разбор в главном процессе. Уровень выставлен в DEBUG
    и propagate отключён намеренно и безусловно: воркер не решает,
    что показывать пользователю — он просто отправляет всё дальше,
    а фильтрация по уровню происходит уже в главном процессе, на
    обработчиках, которые (если) настроило приложение.
    :param queue: Очередь логов, полученная из get_log_queue().
        Если None — логирование в воркере не настраивается.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.handlers.clear()

    if queue is None:
        return

    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(logging.handlers.QueueHandler(queue))


def configure_default_logging(
    log_file: str = LOG_FILE,
    max_bytes: int = MAX_BYTES,
    backup_count: int = BACKUP_COUNT,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> None:
    """
    Опциональная готовая конфигурация логирования: консоль — только
    основные шаги пайплайна (по умолчанию INFO и выше), ротируемый
    файл — всё, включая построчную работу воркеров (по умолчанию
    DEBUG и выше). Нужно вызвать явно — сама библиотека этого не
    делает (см. докстринг модуля).
    Идемпотентна — повторные вызовы не дублируют обработчики.
    :param log_file: Путь к файлу лога.
    :param max_bytes: Размер файла в байтах, при котором происходит ротация.
    :param backup_count: Количество бэкапов при ротации.
    :param console_level: Минимальный уровень записей для консоли.
    :param file_level: Минимальный уровень записей для файла.
    """
    global _default_logging_configured

    if _default_logging_configured:
        return

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    _default_logging_configured = True
