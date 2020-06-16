import asyncio
import inspect
import logging
import uuid
from multiprocessing import Value
from typing import List

import aio_pika
import aio_pika.exceptions

from .base import BaseRPC
from .common import RPCError, RPCHandler, RPCRequest, RPCResponse


class RPC(BaseRPC):
    HEARTBEAT_INTERVAL = 30
    _counter: Value = Value('i', 0)
    _calls: Value = Value('i', 0)
    _consuming: Value = Value('b', False)
    _instances = []

    def __init__(
            self,
            url: str = None,
            name: str = None,
            handler: RPCHandler = None,
            timeout: float = None,
            pool_size: int = 0,
            batch_size: int = 0,
            wait_for_batch: bool = False,
            max_jobs: int = 0,
            jobs_before_die: int = 0,
            loop: asyncio.AbstractEventLoop = None,
    ):
        self._loop = loop
        self._url = url or self.URL
        self._name = name
        self._handler = handler
        self._timeout = timeout
        self._pool_size = pool_size
        self._batch_size = batch_size
        self._wait_for_batch = wait_for_batch
        self._max_jobs = max_jobs
        self._jobs_before_die = jobs_before_die
        self._mconn: aio_pika.RobustConnection = None
        self._mch: aio_pika.RobustChannel = None
        self._mq: aio_pika.RobustQueue = None
        self._queue: asyncio.Queue = asyncio.Queue(loop=self._loop)
        self._pool: List[asyncio.Task] = []
        self._consumer_tag: str = None
        self._instances.append(self)

    def __del__(self):
        self._instances.remove(self)

    @classmethod
    async def close_all(cls):
        tasks = [i.close() for i in cls._instances]
        await asyncio.gather(*tasks)

    async def close(self):
        try:
            if self._mch and not self._mch.is_closed:
                await self._mch.close()
        finally:
            self._mch = None
        try:
            if self._mconn and not self._mconn.is_closed:
                await self._mconn.close()
        finally:
            self._mch = None

    async def _run_pool(self):
        loop = self._loop or asyncio.get_event_loop()
        self._pool = [loop.create_task(self._run_worker()) for _ in range(self._pool_size)]
        await asyncio.gather(*self._pool, loop=self._loop)
        self._pool = []

    async def _run_worker(self):
        bs = self._batch_size
        q = self._queue
        while True:
            if q.empty():
                with self._consuming.get_lock():
                    if self._consuming.value:
                        await asyncio.sleep(0.1, loop=self._loop)
                        continue
                    else:
                        break
            batch = [q.get_nowait()]
            if self._wait_for_batch and bs > 0:
                while len(batch) < bs:
                    if q.empty():
                        with self._consuming.get_lock():
                            if self._consuming.value:
                                await asyncio.sleep(0.1, loop=self._loop)
                                continue
                            else:
                                break
                    batch.append(q.get_nowait())
            else:
                while (bs <= 0 or len(batch) < bs) and not q.empty():
                    batch.append(q.get_nowait())
            await asyncio.wait_for(
                asyncio.ensure_future(
                    self._process_batch(batch), loop=self._loop,
                ),
                self._timeout,
                loop=self._loop,
            )

    async def _autoclose(self):
        while True:
            with self._consuming.get_lock():
                if not self._consuming.value:
                    await self._mq.cancel(self._consumer_tag)
                    break
            await asyncio.sleep(0.1, loop=self._loop)

    async def _wait(self):
        while True:
            with self._consuming.get_lock():
                if not self._consuming.value:
                    break
            await asyncio.sleep(0.1, loop=self._loop)
        while not self._queue.empty():
            await asyncio.sleep(0.1, loop=self._loop)
        while True:
            with self._calls.get_lock():
                if self._calls.value == 0:
                    break
            await asyncio.sleep(0.1, loop=self._loop)

    async def _process_single(self, message: aio_pika.IncomingMessage):
        return await asyncio.wait_for(
            asyncio.ensure_future(
                self._process_batch([message]), loop=self._loop,
            ),
            self._timeout,
            loop=self._loop,
        )

    async def _process_batch(self, messages: List[aio_pika.IncomingMessage]):
        try:
            reqs = []
            for m in messages:
                # logging.debug(f"message: correlation_id={m.correlation_id}")
                req: RPCRequest = self.decode_request(m.body)
                reqs.append(req)
            # logging.debug(f"handler: {self._handler}")
            results = self._handler(*reqs)
            if inspect.isawaitable(results):
                results = await results
        except KeyboardInterrupt:
            with self._consuming.get_lock():
                self._consuming.value = False
            for m in messages:
                await m.reject(requeue=True)
            return
        except Exception as e:
            if len(messages) == 1:
                results = [RPCError()]
                logging.exception(e)
                await messages[0].reject()
            else:
                for m in messages:
                    await asyncio.wait_for(
                        asyncio.ensure_future(
                            self._process_batch([m]), loop=self._loop,
                        ),
                        self._timeout,
                        loop=self._loop,
                    )
                return

        for message, result in zip(messages, results):
            result = aio_pika.Message(
                self.encode_response(result),
                correlation_id=message.correlation_id,
                delivery_mode=message.delivery_mode,
            )
            await self._mch.default_exchange.publish(
                result, routing_key=message.reply_to, mandatory=False,
            )
            if not message.processed:
                await message.ack()

        if self._jobs_before_die:
            with self._counter.get_lock():
                self._counter.value += len(messages)
                value = self._counter.value
            if value >= self._jobs_before_die:
                with self._consuming.get_lock():
                    self._consuming.value = False

    async def consume(self):
        while True:
            try:
                self._mconn = await aio_pika.connect_robust(
                    self._url,
                    loop=self._loop,
                    heartbeat_interval=self.HEARTBEAT_INTERVAL,
                )
                break
            except ConnectionError:
                # This case is not handled by aio-pika by some reasons
                logging.warning("wait for queue...")
                await asyncio.sleep(1, loop=self._loop)

        with self._consuming.get_lock():
            self._consuming.value = True
        self._mch = await self._mconn.channel()

        if self._jobs_before_die:
            if self._max_jobs:
                max_jobs = min(self._max_jobs, self._jobs_before_die)
            else:
                max_jobs = self._jobs_before_die
        else:
            max_jobs = self._max_jobs
        await self._mch.set_qos(prefetch_count=max_jobs)

        self._mq = await self._mch.declare_queue(self._name)

        loop = self._loop or asyncio.get_event_loop()
        loop.create_task(self._autoclose())

        if self._pool_size > 0:
            self._consumer_tag = await self._mq.consume(self._queue.put)
            await self._run_pool()
        else:
            self._consumer_tag = await self._mq.consume(self._process_single)

        await self._wait()
        return self._mconn

    async def call(self, msg: RPCRequest) -> RPCResponse:
        try:
            with self._calls.get_lock():
                self._calls.value += 1
            loop = self._loop or asyncio.get_event_loop()
            return await asyncio.wait_for(
                loop.create_task(self._call(msg)),
                self._timeout,
                loop=self._loop,
            )
        finally:
            with self._calls.get_lock():
                self._calls.value -= 1

    async def _call(self, msg: RPCRequest) -> RPCResponse:
        if not self._mconn:
            self._mconn = await aio_pika.connect_robust(
                self._url,
                loop=self._loop,
                heartbeat_interval=self.HEARTBEAT_INTERVAL,
            )
        if not self._mch:
            self._mch: aio_pika.RobustChannel = await self._mconn.channel()
        mq: aio_pika.RobustQueue = await self._mch.declare_queue()
        try:
            correlation_id = str(uuid.uuid4())
            message = aio_pika.Message(
                self.encode_request(msg),
                correlation_id=correlation_id,
                reply_to=mq.name,
            )
            await self._mch.default_exchange.publish(
                message, routing_key=self._name,
            )
            async with mq.iterator(no_ack=True) as it:
                async for message in it:
                    break
            if message.correlation_id != correlation_id:
                raise ValueError("wrong correlation_id")
            response: RPCResponse = self.decode_response(message.body)
            # logging.debug(f"response: {response}")
            if isinstance(response, RPCError):
                response.reraise()
            return response
        finally:
            await mq.delete(if_empty=False, if_unused=False)
