import asyncio
from typing import AsyncGenerator, Any

async def merge_generators(*gens: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:

    async def run_generator(gen, output_queue, idx):
        try:
            async for item in gen:
                await output_queue.put((idx, item))
        finally:
            await output_queue.put((idx, StopAsyncIteration))

    output_queue = asyncio.Queue()
    tasks = [
        asyncio.create_task(run_generator(gen, output_queue, idx))
        for idx, gen in enumerate(gens)
    ]
    finished = set()

    while len(finished) < len(tasks):
        idx, item = await output_queue.get()
        if item is StopAsyncIteration:
            finished.add(idx)
        else:
            yield item

    # Clean up
    for task in tasks:
        task.cancel()

############################
# TEST.
############################

async def gen1():
    for i in range(3):
        await asyncio.sleep(0.1)
        yield f'gen1: {i}'

async def gen2():
    for i in range(3):
        await asyncio.sleep(0.05)
        yield f'gen2: {i}'

async def main():
    async for item in merge_generators(gen1(), gen2()):
        print(item)

asyncio.run(main())