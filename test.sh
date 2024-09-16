#!/bin/bash
python infer.py \
    --model "dynamic:ext/flan_t5.py:FlanT5" \
    --schema "data/default.json" \
    --device "cpu" \
    --temp 0.1 \
    --output "data/output.csv" \
    --max-length 512 \
    --api-token "<API_TOKEN>" \
    --limit 10000 \
    --limit-prompt 10000 \
    --bf16 \
    --l4b