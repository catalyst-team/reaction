import json
import logging
import os
import re
import sys
import traceback
from typing import Callable, TypeVar

import yaml

RPCRequest = TypeVar('RPCRequest')
RPCResponse = TypeVar('RPCResponse')
RPCHandler = Callable[..., RPCResponse]


class RPCError(Exception):
    def __init__(self):
        self._type = sys.exc_info()[0]
        self._tb = traceback.format_exc()

    def reraise(self):
        raise self._type(self._tb)


def read_config(filename: str):
    if os.path.exists(filename):
        with open(filename) as f:
            data = f.read()
    else:
        data = filename
    path_matcher = re.compile(r'\$\{(.*?)\}')

    def repl(match):
        args = match.group(1).rsplit(':-', 1) + ['']
        name = args[0]
        default = args[1]
        return os.getenv(name, default)

    def path_constructor(loader, node):
        val = path_matcher.sub(repl, node.value)
        try:
            return int(val)
        except:
            pass
        try:
            return float(val)
        except:
            pass
        return val

    yaml.add_implicit_resolver('!path', path_matcher)
    yaml.add_constructor('!path', path_constructor)
    config = yaml.load(data, Loader=yaml.Loader)
    logging.debug(json.dumps(config, indent=4))
    return config
