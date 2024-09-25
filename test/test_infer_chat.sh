#!bin/bash
export PYTHONPATH=$PYTHONPATH:../
python ../fast_cot/infer.py \
    --model "dynamic:ext/flan_t5.py:FlanT5" \
    --schema "../ext/schema/default.json" \
    %% \
    --device "cpu" \
    --temp 0.1