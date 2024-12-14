#!/bin/bash
export PYTHONPATH=$PYTHONPATH:../
python ../bulk_chain/infer.py \
    --schema "../ext/schema/default.json" \
    --adapter "dynamic:ext/flan_t5.py:FlanT5" \
    %%m \
    --device "cpu" \
    --temp 0.1
