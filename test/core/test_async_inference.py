import asyncio

from bulk_chain.api import INFER_MODES
from bulk_chain.core.service_asyncio import AsyncioService
from bulk_chain.core.utils import dynamic_init

DEFAULT_REMOTE_LLM = dynamic_init(class_filepath="../providers/replicate_104.py",
                                  class_name="Replicate")(
    api_token="TOKEN_GOES_HERE",
    model_name="meta/meta-llama-3-8b-instruct",
    stream=True)

im = INFER_MODES["batch_stream_async"]


def wrap_with_index(async_gens):
    async def wrapper(index, agen):
        async for item in agen:
            yield index, item
    return [wrapper(i, agen) for i, agen in enumerate(async_gens)]


print("STARTED!")
for batch in [["a", 'b', "c"], ["d", "e", "f"], ["d", "e", "f"]]:
    gens = im(llm=DEFAULT_REMOTE_LLM, batch=batch)
    for ind, item in AsyncioService.async_gen_to_iter(gen=AsyncioService.merge_generators(*wrap_with_index(gens)), loop=asyncio.get_event_loop()):
        print(ind, str(item))
print("DONE!")
