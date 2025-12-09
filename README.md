# bulk-chain 1.2.0
![](https://img.shields.io/badge/Python-3.9-brightgreen.svg)
[![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nicolay-r/bulk-chain/blob/master/bulk_chain_tutorial.ipynb)
[![twitter](https://img.shields.io/twitter/url/https/shields.io.svg?style=social)](https://x.com/nicolayr_/status/1847969224636961033)
[![PyPI downloads](https://img.shields.io/pypi/dm/bulk-chain.svg)](https://pypistats.org/packages/bulk-chain)

<p align="center">
    <img src="logo.png"/>
</p>

<p align="center">
  <a href="https://github.com/nicolay-r/nlp-thirdgate?tab=readme-ov-file#llm"><b>Third-party providers hosting</b>↗️</a>
  <br>
  <a href="https://github.com/nicolay-r/bulk-chain-shell">👉<b>demo</b>👈</a>
</p>

A no-strings-attached **framework**  for your LLM that allows applying Chain-of-Thought-alike [prompt `schema`](#chain-of-thought-schema) towards a massive textual collections using custom **[third-party providers ↗️](https://github.com/nicolay-r/nlp-thirdgate?tab=readme-ov-file#llm)**.

### Main Features
* ✅ **No-strings**: you're free to LLM dependencies and flexible `venv` customization.
* ✅ **Support schemas descriptions** for Chain-of-Thought concept.
* ✅ **Provides iterator over infinite amount of input contexts**

# Installation

From PyPI: 

```bash
pip install --no-deps bulk-chain
```

or latest version from here:

```bash
pip install git+https://github.com/nicolay-r/bulk-chain@master
```

## Chain-of-Thought Schema

To declare Chain-of-Though (CoT) schema we use `JSON` format. 
The field `schema` is a list of CoT instructions for the Large Language Model.
Each item of the list represent a dictionary with `prompt` and `out` keys that corresponds to the input prompt and output variable name respectively.
All the variable names should be mentioned in `{}`.

**Example**:
```python
[
  {"prompt": "Given customer message: {text}, detect the customer's intent?", "out": "intent" },
  {"prompt": "Given customer message: {text}, extract relevant entities?", "out": "entities"},
  {"prompt": "Given intent: {intent} and entities: {entities}, generate a concise response or action recommendation for support agent.", "out": "action"}
]
```

# Usage

## 🤖 Prepare 

1. [schema](#chain-of-thought-schema)
    * [Example for Sentiment Analysis](test/schema/thor_cot_schema.json)
2. **LLM model** from the [<b>Third-party providers hosting</b>↗️](https://github.com/nicolay-r/nlp-thirdgate?tab=readme-ov-file#llm).
3. Data (iter of dictionaries)

## 🚀 Launch

> **API**: For more details see the [**related Wiki page**](https://github.com/nicolay-r/bulk-chain/wiki)

```python
from bulk_chain.core.utils import dynamic_init
from bulk_chain.api import iter_content

content_it = iter_content(
    # 1. Your schema.              
    schema=[
      {"prompt": "Given customer message: {text}, detect the customer's intent?", "out": "intent" },
      {"prompt": "Given customer message: {text}, extract relevant entities?", "out": "entities"},
      {"prompt": "Given intent: {intent} and entities: {entities}, generate a concise response or action recommendation for support agent.", "out": "action"}
    ],
    # 2. Your third-party model implementation.
    llm=dynamic_init(class_filepath="replicate_104.py")(
       api_token="<API-KEY>",
       model_name="meta/meta-llama-3-70b-instruct"),
    # 3. Customize your inference and result providing modes: 
    infer_mode="batch_async", 
    # 4. Your iterator of dictionaries
    input_dicts_it=YOUR_DATA_IT,
)
    
for content in content_it:
    # Handle your LLM responses here ...
```


# Embed your LLM

All you have to do is to implement `BaseLM` class, that includes:
* `__init__` -- for setting up *batching mode support* and (optional) *model name*;
* **sync modes**:
    * `ask(prompt)` -- infer your model with single prompt;
    * `ask_stream(prompt)` -- returns generator of chunks over inferred result.
* **async modes**:
    * `ask_async(prompt)` 
    * `ask_stream_async(prompt)`

See examples with models [at nlp-thirdgate 🌌](https://github.com/nicolay-r/nlp-thirdgate?tab=readme-ov-file#llm).
