import sys
import traceback
from typing import Callable, TypeVar

RPCRequest = TypeVar('RPCRequest')
RPCResponse = TypeVar('RPCResponse')
RPCHandler = Callable[..., RPCResponse]


class RPCError(Exception):
    def __init__(self):
        self._type = sys.exc_info()[0]
        self._tb = traceback.format_exc()

    def reraise(self):
        raise self._type(self._tb)
