from bulk_chain.api import iter_content
from bulk_chain.core.utils import dynamic_init


# Tested under: https://github.com/nicolay-r/nlp-thirdgate/blob/master/llm/openai_156.py
provider = dynamic_init(class_filepath="providers/openai_156.py")(
    base_url="https://api.novita.ai/openai",
    api_token="<API_TOKEN>",
    model_name="meta-llama/llama-3.3-70b-instruct")

content_it = iter_content(
    # 1. Your schema.              
    schema=[
      {"prompt": "extract topic: {text}", "out": "topic" },
      {"prompt": "extract subject: {text}", "out": "subject"},
    ],
    # 2. Your third-party model implementation.
    llm=provider,
    batch_size=10,
    # 3. Customize your inference and result providing modes: 
    infer_mode="batch_async",
    # 4. Your iterator of dictionaries
    input_dicts_it=[
        { "text": "Rocks are hard" },
        { "text": "Water is wet" },
        { "text": "Fire is hot" }
    ],
)

for batch in content_it:
    for entry in batch:
        print(entry)