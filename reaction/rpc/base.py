import inspect
import pickle
from abc import ABC, abstractmethod

from .common import RPCHandler, RPCRequest, RPCResponse


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

    def _bind(self, instance):
        self._instance = instance
        return self._handler

    def __call__(self, handler: RPCHandler) -> RPCHandler:
        self._handler = handler
        if self._name is None:
            self._name = handler.__name__
        handler.consume = self.consume
        handler.call = self.call
        handler.bind = self._bind
        return handler
