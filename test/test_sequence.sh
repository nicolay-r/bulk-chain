#!bin/bash
export PYTHONPATH=$PYTHONPATH:../
python ../fast_cot/infer.py \
    --model "dynamic:ext/flan_t5.py:FlanT5" \
    --src "data/sample.csv" \
    --schema "../ext/schema/thor_cot_schema.json" \
    --device "cpu" \
    --temp 0.1