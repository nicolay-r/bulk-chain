#!/bin/bash
export PYTHONPATH=$PYTHONPATH:../
python ../fast_cot/infer.py \
    --src "data/sample.jsonl" \
    --schema "../ext/schema/thor_cot_schema.json" \
    --adapter "dynamic:ext/flan_t5.py:FlanT5" \
    %% \
    --device "cpu" \
    --temp 0.1
