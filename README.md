# fast-cot
![](https://img.shields.io/badge/Python-3.9-brightgreen.svg)

No-strings tiny **Chain-of-Thought framework** for your Large Language Model (LLM) that saves you time ⏰ and money 💰

The end goal of this framework is to serve chain of prompts (a.k.a. Chain-of-Thought) formed into `schema` towards LLM.
It iterates through your data stored in `CSV`/`JSONL`/`sqlite`.

### Features
* **Provides iterator over infinite amount of input contexts** served in `CSV`/`JSONL`.
* **Caching progress**: withstanding exception during LLM calls by using `sqlite3` engine for caching LLM answers;
* **Support schemas descriptions** for Chain-of-Thought concept.

# Installation

```bash
pip install git+https://github.com/nicolay-r/fast-cot@master
```

# Usage

Just **three** simple steps:

1. Define your sequence of prompts with their dependencies
   * **For example:** [Three-hop-Reasoning in Implicit CoT](https://arxiv.org/pdf/2305.11255.pdf) for sentiment analysis at 
     [`ext/schema/thor_cot_schema.json`](/ext/schema/thor_cot_schema.json)
   * Or fetch  
    ```bash
    !wget https://raw.githubusercontent.com/nicolay-r/fast-cot/refs/heads/master/ext/schema/default.json
    ```
2. Fetch or write your own **model**:
```bash
!wget https://raw.githubusercontent.com/nicolay-r/fast-cot/refs/heads/master/ext/flan_t5.py
```

3. Launch inference:
```bash
python infer.py --model "dynamic:flan_t5.py:FlanT5" --schema "default.json" --device "cpu" --temp 0.1
```

## Implement your model

All you have to do is to implement `BaseLM` class, that includes:
* `__init__` -- for initialization;
* `ask(prompt)` -- infer your model with the given `prompt`. 

See examples with models [here](/ext).