import asyncio
from typing import AsyncGenerator, Any


class AsyncioService:

    @staticmethod
    async def _run_tasks_async(batch, async_handler):
        tasks = [async_handler(prompt) for prompt in batch]
        return await asyncio.gather(*tasks)

    @staticmethod
    async def _run_generator(gen, output_queue, idx):
        try:
            async for item in gen:
                await output_queue.put((idx, item))
        finally:
            await output_queue.put((idx, StopAsyncIteration))


    @staticmethod
    def run_tasks(event_loop, **tasks_kwargs):
        return event_loop.run_until_complete(AsyncioService._run_tasks_async(**tasks_kwargs))

    @staticmethod
    async def merge_generators(*gens: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:

        output_queue = asyncio.Queue()
        tasks = [
            asyncio.create_task(AsyncioService._run_generator(gen, output_queue, idx))
            for idx, gen in enumerate(gens)
        ]

        finished = set()
        while len(finished) < len(tasks):
            idx, item = await output_queue.get()
            if item is StopAsyncIteration:
                finished.add(idx)
            else:
                yield item

        for task in tasks:
            task.cancel()

    @staticmethod
    def async_gen_to_iter(gen, loop=None):
        """ This approach is limited. Could be considered as legacy.
            https://stackoverflow.com/questions/71580727/translating-async-generator-into-sync-one/78573267#78573267
        """

        loop_created = False
        if loop is None:
            loop_created = True
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)
        try:
            while True:
                try:
                    yield loop.run_until_complete(gen.__anext__())
                except StopAsyncIteration:
                    break
        finally:
            if loop_created:
                loop.close()
