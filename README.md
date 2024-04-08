# quick_cot
No-strings tiny Chain-of-Thought framework for your Large Language Model (LLM) that saves you time ⏰ and money 💰

This applies sequence of prompts towards your data in `csv`/`json`/`sqlite` in order to expand table and export it:

TODO. Features:
* First feature.
* Second feature.
* Third feature.

# Usage

Just **two** simple steps:

1. Define your sequence of prompts with their dependencies
   * For example: [Three-hop-Reasoning in Implicit CoT](https://arxiv.org/pdf/2305.11255.pdf) for sentiment analysis at 
     [`data/thor_cot_schema.json`](/data/thor_cot_schema.json)
2. Launch inference:
```bash
python infer.py \
    --model "google/flan-t5-base" \
    --schema "data/thor_cot_schema.json" \
    --prompt "rusentne2023_default_en" \
    --device "cpu" \
    --temp 0.1 \
    --output "data/output.csv" \
    --max-length 512 \
    --hf-token "<YOUR_HUGGINGFACE_TOKEN>" \
    --openai-token "<YOUR_OPENAI_TOKEN>" \
    --limit 10000 \
    --limit-prompt 10000 \
    --bf16 \
    --l4b
```

## Embed your model