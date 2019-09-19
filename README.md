# reaction

## Quick start

**consumer.py**:
```python
import asyncio
from typing import List, Any
from reaction.rpc import RabbitRPC


class rpc(RabbitRPC):
    URL = 'amqp://user:password@host'


@rpc()
def sync_square(*values) -> List[float]:
    return [v ** 2 for v in values]


@rpc()
async def async_square(*values) -> List[float]:
    await asyncio.sleep(1)
    return [v ** 2 for v in values]


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(sync_square.consume())
    loop.create_task(async_square.consume())
    loop.run_forever()
```

**client.py**:
```python
import asyncio
from consumer import sync_square, async_square

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    x = loop.run_until_complete(sync_square.call(2, 3))
    y = loop.run_until_complete(async_square.call(4, 5, 6))
    print(x)  # 4, 9
    print(y)  # 16, 25, 36
    loop.close()
```

## Example
* `cd example && docker-compose up --force-recreate --build`
* RabbitMQ web ui: http://127.0.0.1:15672/#/
  * user: admin
  * password: j8XfG9ZDT5ZZrWTzw62q
* Docs (you can submit requests from web ui): http://127.0.0.1:8000/docs#/
* Redoc: http://127.0.0.1:8000/redoc
