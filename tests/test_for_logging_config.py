import logging
import logging.handlers
import multiprocessing as mp

from flowmaputility import logging_config
from flowmaputility.logging_config import (
    LOGGER_NAME,
    configure_worker_logging,
    setup_logging,
)


def test_setup_logging_is_idempotent():
    queue_first = setup_logging()
    queue_second = setup_logging()
    assert queue_first is queue_second

    logger = logging.getLogger(LOGGER_NAME)
    assert len(logger.handlers) == 2


def test_setup_logging_handler_levels():
    setup_logging()
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


def test_setup_logging_returns_multiprocessing_queue():
    queue = setup_logging()
    assert isinstance(queue, type(mp.Queue()))


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
