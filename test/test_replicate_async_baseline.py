from timeit import default_timer as timer
from utils import default_remote_llm


llm = default_remote_llm()

start = timer()
r = ["".join([str(s) for s in llm.ask(f"what's the color of the {p}")])
     for p in ["sky", "ground", "water"]]
end = timer()

total = sum(len(i) for i in r)
print(f"Completed [time: {end - start}]: {len(r[0])}, {len(r[1])}, {len(r[2])}")
print(f"TPS: {total / (end-start)}")
