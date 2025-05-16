from timeit import default_timer as timer
from utils import DEFAULT_REMOTE_LLM

start = timer()
r = ["".join([str(s) for s in DEFAULT_REMOTE_LLM.ask(f"what's the color of the {p}")])
     for p in ["sky", "ground", "water"]]
end = timer()

total = sum(len(i) for i in r)
print(f"Completed [time: {end - start}]: {len(r[0])}, {len(r[1])}, {len(r[2])}")
print(f"TPS: {total / (end-start)}")
