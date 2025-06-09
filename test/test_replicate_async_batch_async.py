from timeit import default_timer as timer
import asyncio

from utils import default_remote_llm


llm = default_remote_llm()


async def infer_item(prompt):
    content = []
    for chunk in llm.ask(prompt):
        content.append(str(chunk))
    return content


async def coro_infer_llm(prompt):
    print(f"launch: {prompt}")
    r = None
    for response in asyncio.as_completed([infer_item(prompt)]):
        r = await response
    return "".join(r)


async def main():
    batch = [f"what's the color of the {p}" for p in ["sky", "ground", "water"]]
    routines = [coro_infer_llm(p) for p in batch]
    return await asyncio.gather(*routines)


start = timer()
r = asyncio.run(main())
end = timer()

total = sum(len(i) for i in r)
print(r[0])
print(r[1])
print(r[2])
print(f"Completed [time: {end - start}]: {len(r[0])}, {len(r[1])}, {len(r[2])}")
print(f"TPS: {total / (end-start)}")
