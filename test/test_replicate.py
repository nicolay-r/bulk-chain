import asyncio
from replicate.client import Client


model_version = "meta/meta-llama-3-70b-instruct"

prompts = [
    f"A chariot pulled by a team of {count} rainbow unicorns"
    for count in ["two", "three", "four", "five", "six", "seven"]
]


async def replicate_infer_prompts_async():
    tasks = [
        client.async_run(model_version, input={"prompt": prompt})
        for prompt in prompts
    ]
    
    return await asyncio.gather(*tasks)

client = Client(api_token="<YOUR-TOKEN-GOES-HERE>")
results = asyncio.run(replicate_infer_prompts_async())

# Process results
for i, result in enumerate(results):
    print(f"Prompt: {prompts[i]}")
    print(f"Result: {''.join(result)}\n")
