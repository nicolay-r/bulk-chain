from timeit import default_timer as timer

from bulk_chain.core.utils import dynamic_init
from utils import API_TOKEN


llm = dynamic_init(class_filepath="providers/replicate_104.py",
                   class_name="Replicate")(api_token=API_TOKEN,
                                           model_name="meta/meta-llama-3-8b-instruct",
                                           stream=True)

start = timer()
r = ["".join([str(s) for s in llm.ask(f"what's the color of the {p}")]) for p in ["sky", "ground", "water"]]
end = timer()

total = sum(len(i) for i in r)
print(f"Completed [time: {end - start}]: {len(r[0])}, {len(r[1])}, {len(r[2])}")
print(f"TPS: {total / (end-start)}")
