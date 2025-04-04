#!/bin/bash
export PYTHONPATH=$PYTHONPATH:../

python ../bulk_chain/infer.py \
    --schema "schema/default.json" \
    --adapter "dynamic:providers/replicate_104.py:Replicate" \
    %%m \
    --model_name "deepseek-ai/deepseek-r1" \
    --api_token "<REPLICATE-API-TOKEN>"
