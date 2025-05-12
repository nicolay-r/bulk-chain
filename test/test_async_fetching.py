import asyncio
from bulk_chain.core.service_asyncio import AsyncioService


async def gen1():
    for i in range(3):
        await asyncio.sleep(0.1)
        yield f'gen1: {i}'


async def gen2():
    for i in range(3):
        await asyncio.sleep(0.05)
        yield f'gen2: {i}'


# This is an async version.
async def main():
    async for item in AsyncioService.merge_generators(gen1(), gen2()):
        # TODO. This is what could be already used with fastAPI.
        # TODO. We can yield this content instead of printing.
        print(item)


# This is sync version.
asyncio.run(main())

print("_____________")
for item in AsyncioService.async_gen_to_iter(gen=AsyncioService.merge_generators(gen1(), gen2()), loop=None):
    print(item)