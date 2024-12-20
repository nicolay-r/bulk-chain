# bulk-chain 0.24.3
![](https://img.shields.io/badge/Python-3.9-brightgreen.svg)
[![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nicolay-r/bulk-chain/blob/master/bulk_chain_tutorial.ipynb)
[![twitter](https://img.shields.io/twitter/url/https/shields.io.svg?style=social)](https://x.com/nicolayr_/status/1847969224636961033)
[![PyPI downloads](https://img.shields.io/pypi/dm/bulk-chain.svg)](https://pypistats.org/packages/bulk-chain)

<p align="center">
    <img src="logo.png"/>
</p>

A lightweight, no-strings-attached **framework**  for your LLM that allows applying [Chain-of-Thought](https://arxiv.org/abs/2201.11903)-alike prompt `schema` (See [related section](#chain-of-thought-schema)) towards a massive textual collections.

### Main Features
* ✅ **No-strings**: you're free to LLM dependencies and flexible `venv` customization.
* ✅ **Support schemas descriptions** for Chain-of-Thought concept.
* ✅ **Provides iterator over infinite amount of input contexts** served in `CSV`/`JSONL`.

### Extra Features
* ✅ **Progress caching [for remote LLMs]**: withstanding exception during LLM calls by using `sqlite3` engine for caching LLM answers;


# Installation

From PyPI: 

```bash
pip install bulk-chain
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

Another templates are available [here](/ext/schema/thor_cot_schema.json).

# Usage

Just **three** simple steps:

1. Define your [CoT Schema](#chain-of-thought-schema), or fetch it as shown below:
```bash
!wget https://raw.githubusercontent.com/nicolay-r/bulk-chain/refs/heads/master/ext/schema/default.json
```
2. Fetch or write your own **model** or pick the one [preset here](/ext/):
```bash
!wget https://raw.githubusercontent.com/nicolay-r/bulk-chain/refs/heads/master/ext/flan_t5.py
```

3. Launch inference in (chat mode):
```bash
!python -m bulk_chain.infer \
    --schema "default.json" \
    --adapter "dynamic:flan_t5.py:FlanT5" \
    %%m \
    --device "cpu" \
    --temp 0.1
```

# Embed your LLM

All you have to do is to implement `BaseLM` class, that includes:
* `__init__` -- for initialization;
* `ask(prompt)` -- infer your model with the given `prompt`.

See examples with models [here](/ext).
