# quick_cot
![](https://img.shields.io/badge/Python-3.9-brightgreen.svg)

No-strings tiny **Chain-of-Thought framework** for your Large Language Model (LLM) that saves you time ⏰ and money 💰

This applies sequence of prompts towards your data in `CSV`/`JSONL`/`sqlite` in order to expand table and export it:

### Features
* **Provides iterator over infinite amount of input contexts** served in `CSV`/`JSONL`.
* **Caching progress**: withstanding exception during LLM calls by using `sqlite3` engine for caching LLM answers;
* **Support schemas descriptions** for Chain-of-Thought concept.

# Installation

> pip3 install -r dependencies.txt 

# Usage

Just **two** simple steps:

1. Define your sequence of prompts with their dependencies
   * **For example:** [Three-hop-Reasoning in Implicit CoT](https://arxiv.org/pdf/2305.11255.pdf) for sentiment analysis at 
     [`data/thor_cot_schema.json`](/data/thor_cot_schema.json)
2. Launch inference:
```bash
python infer.py \
    --model "google/flan-t5-base" \
    --schema "data/thor_cot_schema.json" \
    --device "cpu" \
    --temp 0.1 \
    --output "data/output.csv" \
    --max-length 512 \
    --api-token "<API_TOKEN>" \
    --limit 10000 \
    --limit-prompt 10000 \
    --bf16 \
    --l4b
```

## Embed your model

> TODO. To be updated.