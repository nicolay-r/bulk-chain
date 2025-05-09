import asyncio


class AsyncioService:

    @staticmethod
    async def _run_tasks_async(batch, async_handler):
        tasks = [async_handler(prompt) for prompt in batch]
        return await asyncio.gather(*tasks)

    @staticmethod
    def run_tasks(**tasks_kwargs):
        return asyncio.get_event_loop().run_until_complete(
            AsyncioService._run_tasks_async(**tasks_kwargs)
        )
