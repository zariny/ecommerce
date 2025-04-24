"""
	Chain of Responsibility
	a behavioral design pattern that lets you pass requests along a chain of handlers.
	    Upon receiving a request, each handler decides either to process the request or to pass
	    it to the next handler in the chain.
"""


import abc


class AbstractHandler(abc.ABC):
    _next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abc.abstractmethod
    def handle(self, flag):
        return self._next_handler.handle(flag) if self._next_handler else flag
