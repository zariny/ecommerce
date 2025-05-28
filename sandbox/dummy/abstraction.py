"""
	Chain of Responsibility
	a behavioral design pattern that lets you pass requests along a chain of handlers.
	    Upon receiving a request, each handler decides either to process the request or to pass
	    it to the next handler in the chain.
"""
from faker import Faker
import abc
import logging
import random


__all__ = ["Faker", "random", "AbstractHandler"]


class Formatter(logging.Formatter):
    blue = "\x1b[34m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(levelname)s - %(name)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: blue + format + reset,
        logging.INFO: blue + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class AbstractHandler(abc.ABC):
    _next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @property
    def logger(self):
        logger = logging.Logger(name="Dummy-Data-Logger")
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(Formatter())
        stream_handler.setLevel(logging.INFO)
        logger.addHandler(stream_handler)
        logger.setLevel(logging.INFO)
        return logger

    @abc.abstractmethod
    def handle(self, flag, **kwargs):
        if not flag:
            self.logger.error(f"Handler chain interrupted at '{self.__class__.__name__}' due to flag=False.")
        if self._next_handler:
            self._next_handler.handle(flag, **kwargs)
        else:
            self.logger.info("Successfully completed.")
            self.logger.warning("Use createdummydata only one time!")
        return flag
