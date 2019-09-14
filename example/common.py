import logging

from fastapi import FastAPI

from reaction.__version__ import __version__

logging.basicConfig(level=logging.DEBUG)

rpc_uri = 'amqp://admin:j8XfG9ZDT5ZZrWTzw62q@queue'
app = FastAPI(debug=True, title='Reaction Example', version=__version__)
