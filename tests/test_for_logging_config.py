import logging
import logging.handlers
import multiprocessing as mp
import time

import pytest

from flowmaputility import logging_config
from flowmaputility.logging_config import (
    LOGGER_NAME,
    configure_default_logging,
    configure_worker_logging,
    get_log_queue,
    start_queue_listener,
)


def test_null_handler_attached_by_default():
    logger = logging.getLogger(LOGGER_NAME)
    assert any(isinstance(h, logging.NullHandler) for h in logger.handlers)


def test_get_log_queue_does_not_touch_handlers_or_propagate():
    logger = logging.getLogger(LOGGER_NAME)
    handlers_before = logger.handlers[:]
    propagate_before = logger.propagate

    get_log_queue()

    assert logger.handlers == handlers_before
    assert logger.propagate == propagate_before


def test_get_log_queue_is_idempotent():
    queue_first = get_log_queue()
    queue_second = get_log_queue()
    assert queue_first is queue_second


def test_start_queue_listener_requires_get_log_queue_first():
    with pytest.raises(RuntimeError):
        start_queue_listener()


def test_start_queue_listener_is_idempotent():
    get_log_queue()
    start_queue_listener()
    listener = logging_config._listener

    start_queue_listener()

    assert logging_config._listener is listener
    assert logging_config._listener_started is True
    assert listener._thread is not None


def test_queue_records_are_routed_through_real_logger():
    """
    Запись из очереди (как если бы её положил воркер) должна попасть в
    реальный логгер "flowmaputility" в главном процессе — то есть
    подчиниться тем обработчикам, которые (если) настроило приложение,
    а не какому-то отдельному фиксированному набору обработчиков.

    Кладём LogRecord в очередь вручную, а не через
    configure_worker_logging: в реальности воркер и главный процесс —
    это разные процессы с разными копиями логгера, а в тесте (один
    процесс) настройка воркера очистила бы и обработчик, который мы
    тут проверяем.
    """
    queue = get_log_queue()
    start_queue_listener()

    logger = logging.getLogger(LOGGER_NAME)
    original_level = logger.level
    captured = []
    handler = logging.Handler()
    handler.emit = captured.append
    logger.addHandler(handler)
    try:
        # Разрешаем DEBUG явно — как это сделал бы configure_default_logging()
        # или само приложение. Без этого запись отфильтровалась бы уже
        # на уровне логгера, см. test_queue_respects_logger_effective_level.
        logger.setLevel(logging.DEBUG)
        record = logging.LogRecord(
            name=LOGGER_NAME,
            level=logging.DEBUG,
            pathname=__file__,
            lineno=1,
            msg="hello from worker",
            args=(),
            exc_info=None,
        )
        queue.put(record)

        for _ in range(50):
            if captured:
                break
            time.sleep(0.05)
    finally:
        logger.removeHandler(handler)
        logger.setLevel(original_level)

    assert any(r.getMessage() == "hello from worker" for r in captured)


def test_queue_respects_logger_effective_level():
    """
    Регрессия на конкретный баг: Logger.handle() сам по себе НЕ
    проверяет эффективный уровень логгера, поэтому DEBUG-записи из
    воркеров (они шлют всё безусловно) могли бы пролезать мимо
    уровня, который явно выставило приложение (или мы через
    configure_default_logging). Роутер обязан фильтровать сам.
    """
    queue = get_log_queue()
    start_queue_listener()

    logger = logging.getLogger(LOGGER_NAME)
    original_level = logger.level
    captured = []
    handler = logging.Handler()
    handler.emit = captured.append
    logger.addHandler(handler)
    try:
        logger.setLevel(logging.WARNING)

        def _put(level: int, msg: str) -> None:
            queue.put(
                logging.LogRecord(
                    name=LOGGER_NAME,
                    level=level,
                    pathname=__file__,
                    lineno=1,
                    msg=msg,
                    args=(),
                    exc_info=None,
                )
            )

        _put(logging.DEBUG, "should be dropped")
        _put(logging.WARNING, "should pass")

        for _ in range(50):
            if captured:
                break
            time.sleep(0.05)
    finally:
        logger.removeHandler(handler)
        logger.setLevel(original_level)

    messages = [r.getMessage() for r in captured]
    assert "should pass" in messages
    assert "should be dropped" not in messages


def test_configure_worker_logging_attaches_queue_handler():
    queue = mp.Queue()
    configure_worker_logging(queue)
    logger = logging.getLogger(LOGGER_NAME)

    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.handlers.QueueHandler)
    assert logger.level == logging.DEBUG
    assert logger.propagate is False


def test_configure_worker_logging_without_queue_clears_handlers():
    logger = logging.getLogger(LOGGER_NAME)
    logger.addHandler(logging.NullHandler())

    configure_worker_logging(None)

    assert logger.handlers == []


def test_configure_default_logging_attaches_console_and_file_handlers():
    configure_default_logging()
    logger = logging.getLogger(LOGGER_NAME)

    console_handlers = [
        h for h in logger.handlers if type(h) is logging.StreamHandler
    ]
    file_handlers = [
        h
        for h in logger.handlers
        if isinstance(h, logging.handlers.RotatingFileHandler)
    ]

    assert len(console_handlers) == 1
    assert console_handlers[0].level == logging.INFO

    assert len(file_handlers) == 1
    assert file_handlers[0].level == logging.DEBUG
    assert file_handlers[0].maxBytes == logging_config.MAX_BYTES
    assert file_handlers[0].backupCount == logging_config.BACKUP_COUNT


def test_configure_default_logging_is_idempotent():
    configure_default_logging()
    logger = logging.getLogger(LOGGER_NAME)
    handler_count = len(logger.handlers)

    configure_default_logging()

    assert len(logger.handlers) == handler_count


def test_configure_default_logging_does_not_disable_propagate():
    configure_default_logging()
    logger = logging.getLogger(LOGGER_NAME)
    assert logger.propagate is True
