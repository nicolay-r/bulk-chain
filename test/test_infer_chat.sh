#!bin/bash
export PYTHONPATH=$PYTHONPATH:../
python ../fast_cot/infer.py \
    --schema "../ext/schema/default.json" \
    --adapter "dynamic:ext/flan_t5.py:FlanT5" \
    %% \
    --device "cpu" \
    --temp 0.1