import asyncio
import queue
import threading
from typing import AsyncGenerator, Any, Iterator


class ThreadingService:
    @staticmethod
    def async_gen_to_iter(gen: AsyncGenerator[Any, None]) -> Iterator[Any]:
        q = queue.Queue()
        sentinel = object()

        def runner():
            async def consume():
                try:
                    async for item in gen:
                        q.put(item)
                finally:
                    q.put(sentinel)

            asyncio.run(consume())

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

        while True:
            item = q.get()
            if item is sentinel:
                break
            yield item
