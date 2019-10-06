import functools
import pickle
from abc import ABC, abstractmethod

from .common import RPCHandler, RPCRequest, RPCResponse, read_config


class FunctionOrMethod:
    def __init__(self, func, **attrs):
        self._func = func
        self._attrs = attrs
        self._method = False

    def __getattr__(self, item):
        return self._attrs.get(item)

    def __get__(self, instance, owner):
        if not self._method:
            self._func = functools.partial(self._func, instance)
            self._method = True
        return self

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)


class BaseRPC(ABC):
    @staticmethod
    def encode_request(val: RPCRequest) -> bytes:
        return pickle.dumps(val)

    @staticmethod
    def decode_request(val: bytes) -> RPCRequest:
        return pickle.loads(val)

    @staticmethod
    def encode_response(val: RPCResponse) -> bytes:
        return pickle.dumps(val)

    @staticmethod
    def decode_response(val: bytes) -> RPCResponse:
        return pickle.loads(val)

    @abstractmethod
    async def consume(self):
        pass

    @abstractmethod
    async def call(self, msg: RPCRequest) -> RPCResponse:
        pass

    def __call__(self, handler: RPCHandler) -> RPCHandler:
        if self._name is None:
            self._name = handler.__name__
        self._handler = FunctionOrMethod(
            handler,
            consume=self.consume,
            call=self.call,
        )
        return self._handler

    @classmethod
    def configure(cls, filename: str) -> 'BaseRPC':
        config = read_config(filename)
        return cls(**config)
