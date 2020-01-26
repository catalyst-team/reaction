<div align="center">

![Reaction logo](https://raw.githubusercontent.com/catalyst-team/catalyst-pics/master/pics/Reaction_Logo.png)

**Convenient DL serving**

[![Build Status](https://travis-ci.com/catalyst-team/reaction.svg?branch=master)](https://travis-ci.com/catalyst-team/reaction)
[![Pipi version](https://img.shields.io/pypi/v/reaction.svg)](https://pypi.org/project/reaction/)
[![Docs](https://img.shields.io/badge/dynamic/json.svg?label=docs&url=https%3A%2F%2Fpypi.org%2Fpypi%2Freaction%2Fjson&query=%24.info.version&colorB=brightgreen&prefix=v)](https://catalyst-team.github.io/reaction/index.html)
[![PyPI Status](https://pepy.tech/badge/reaction)](https://pepy.tech/project/reaction)
[![Github contributors](https://img.shields.io/github/contributors/catalyst-team/reaction.svg?logo=github&logoColor=white)](https://github.com/catalyst-team/reaction/graphs/contributors)

[![Twitter](https://img.shields.io/badge/news-on%20twitter-499feb)](https://t.me/catalyst_team)
[![Telegram](https://img.shields.io/badge/channel-on%20telegram-blue)](https://t.me/catalyst_team)
[![Spectrum](https://img.shields.io/badge/chat-on%20spectrum-blueviolet)](https://spectrum.chat/catalyst)
[![Slack](https://img.shields.io/badge/ODS-slack-red)](https://opendatascience.slack.com/messages/CGK4KQBHD)

</div>

Part of [Catalyst Ecosystem](https://docs.google.com/presentation/d/1D-yhVOg6OXzjo9K_-IS5vSHLPIUxp1PEkFGnpRcNCNU/edit?usp=sharing). Project [manifest](https://github.com/catalyst-team/catalyst/blob/master/MANIFEST.md).

---

## Installation

Common installation:
```bash
pip install -U reaction
```

## Getting started

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
* Register telegram bot, achieve token
* `cd example && TG_TOKEN="telegram bot token goes here" docker-compose up --force-recreate --build`
* RabbitMQ web ui: http://127.0.0.1:15672/#/
  * user: admin
  * password: j8XfG9ZDT5ZZrWTzw62q
* Docs (you can submit requests from web ui): http://127.0.0.1:8000/docs#/
* Redoc: http://127.0.0.1:8000/redoc
* Telegram bot is ready to classify ants & bees, but you have to send files "as a photo"

## Telegram bot quick howto

Install async telegram client first:
```bash
$ pip install aiotg
```

Then create your bot:

**tgbot.py**
```python
from consumer import async_square
from aiotg import Bot, Chat

bot = Bot(api_token='telegram bot token goes here')


@bot.command('/start')
async def start(chat: Chat, match):
    return chat.reply('Send me /square command with one float argument')


@bot.command(r"/square (.+)")
async def square_command(chat: Chat, match):
    val = match.group(1)
    try:
        val = float(val)
        square = await async_square.call(val)
        resp = f'Square for {val} is {square}'
    except:
        resp = 'Invalid number'
    return chat.reply(resp)


bot.run()
```
