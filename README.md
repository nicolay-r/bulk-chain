# bulk-chain 0.25.3
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
  <a href="https://github.com/nicolay-r/bulk-chain/blob/master/README.md#demo-mode">👉<b>demo</b>👈</a>
</p>

A no-strings-attached **framework**  for your LLM that allows applying Chain-of-Thought-alike [prompt `schema`](#chain-of-thought-schema) towards a massive textual collections using custom **[third-party providers ↗️](https://github.com/nicolay-r/nlp-thirdgate?tab=readme-ov-file#llm)**.

### Main Features
* ✅ **No-strings**: you're free to LLM dependencies and flexible `venv` customization.
* ✅ **Support schemas descriptions** for Chain-of-Thought concept.
* ✅ **Provides iterator over infinite amount of input contexts** served in `CSV`/`JSONL`.

### Extra Features
* ✅ **Progress caching [for remote LLMs]**: withstanding exception during LLM calls by using `sqlite3` engine for caching LLM answers;


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

To declare Chain-of-Though (CoT) schema, this project exploits `JSON` format.
This format adopts `name` field for declaring a name and `schema` is a list of CoT instructions for the Large Language Model.

Each step represents a dictionary with `prompt` and `out` keys that corresponds to the input prompt and output variable name respectively.
All the variable names are expected to be mentioned in `{}`.

Below, is an example on how to declare your own schema:

```python
{
"name": "schema-name",
"schema": [
    {"prompt": "Given the question '{text}', let's think step-by-step.", 
     "out": "steps"},
    {"prompt": "For the question '{text}' the reasoining steps are '{steps}'. what would be an answer?", 
     "out":  "answer"},
]
}
```

# Usage

Preliminary steps:

1. Define your [schema](#chain-of-thought-schema) ([Example for Sentiment Analysis](/ext/schema/thor_cot_schema.json)))
2. Wrap or pick **LLM model** from the [<b>Third-party providers hosting</b>↗️](https://github.com/nicolay-r/nlp-thirdgate?tab=readme-ov-file#llm).

## Shell

### Demo Mode

**demo mode** to interact with LLM via command line with LLM output streaming support. 
The video below illustrates an example of application for sentiment analysis on author opinion extraction towards mentioned object in text.

Quck start with launching demo:
1. ⬇️ Download [replicate](https://replicate.com/) provider for `bulk-chain`:
2. 📜 Setup your reasoning `thor_cot_schema.json` according to the [following example ↗️](test/schema/thor_cot_schema.json)
3. 🚀 Launch `demo.py` as follows:
```bash
python3 -m bulk_chain.demo \
    --schema "test/schema/thor_cot_schema.json" \
    --adapter "dynamic:replicate_104.py:Replicate" \
    %%m \
    --model_name "meta/meta-llama-3-70b-instruct" \
    --api_token "<REPLICATE-API-TOKEN>" \
    --stream
```

📺 This video showcase application of the [↗️ Sentiment Analysis Schema](https://github.com/nicolay-r/bulk-chain/blob/master/test/schema/thor_cot_schema.json) towards [LLaMA-3-70B-Instruct](https://replicate.com/meta/meta-llama-3-70b-instruct) hosted by Replicate for reasoning over submitted texts
![sa-bulk-chain-cot-final](https://github.com/user-attachments/assets/0cc8fdcb-6ddb-44a3-8f05-d76250ae6423)


### Inference Mode

> **NOTE:** You have to install `source-iter` and `tqdm` packages that actual [dependencies](dependencies.txt) of this project

1. ⬇️ Download [replicate](https://replicate.com/) provider for `bulk-chain`:
```bash
wget https://raw.githubusercontent.com/nicolay-r/nlp-thirdgate/refs/heads/master/llm/replicate_104.py
```
2. 📜 Setup your reasoning `schema.json` according to the [following example ↗️](test/schema/default.json)
3. 🚀 Launch inference using `DeepSeek-R1`:
```bash
python3 -m bulk_chain.infer \
    --src "<PATH-TO-YOUR-CSV-or-JSONL>" \
    --schema "test/schema/default.json" \
    --adapter "replicate_104.py:Replicate" \
    %%m \
    --model_name "deepseek-ai/deepseek-r1" \
    --api_token "<REPLICATE-API-TOKEN>"
```

## API

Please take a look at the [**related Wiki page**](https://github.com/nicolay-r/bulk-chain/wiki)


# Embed your LLM

All you have to do is to implement `BaseLM` class, that includes:
* `__init__` -- for setting up *batching mode support* and (optional) *model name*;
* `ask(prompt)` -- infer your model with the given `prompt`.

See examples with models [at nlp-thirdgate 🌌](https://github.com/nicolay-r/nlp-thirdgate?tab=readme-ov-file#llm).
