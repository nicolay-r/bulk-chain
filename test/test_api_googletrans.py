from bulk_chain.api import iter_content
from bulk_chain.core.utils import dynamic_init


provider = dynamic_init(class_filepath="providers/googletrans_402.py")()

content_it = iter_content(
    # 1. Your schema.              
    schema=[
      {"prompt": "{text}", "out": "fr"},
    ],
    # 2. Your third-party model implementation.
    llm=provider,
    batch_size=10,
    # 3. Toggle streaming if needed
    stream=False,
    # 4. Toggle asynchronous mode if needed
    async_mode=True,
    async_policy='batch',
    # 5. Your iterator of dictionaries
    input_dicts_it=[
        {"text": "Rocks are hard"},
        {"text": "Water is wet"},
        {"text": "Fire is hot"},
        {"text": "Fire is hot"},
        {"text": "Fire is hot"},
        {"text": "Fire is hot"}
    ],
)

for batch in content_it:
    for entry in batch:
        print(entry)