import asyncio
import queue
import threading
from typing import AsyncGenerator, Any, Iterator


class ThreadingService:

    @staticmethod
    def async_gen_to_iter(async_gen: AsyncGenerator[Any, None]) -> Iterator[Any]:
        q = queue.Queue()
        sentinel = object()

        def runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def consume():
                try:
                    async for item in async_gen:
                        q.put(item)
                finally:
                    q.put(sentinel)

            try:
                loop.run_until_complete(consume())
            finally:
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

        while True:
            item = q.get()
            if item is sentinel:
                break
            yield item