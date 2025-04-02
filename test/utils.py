import json
from os.path import join, dirname, realpath

API_TOKEN = "<API_TOKEN_GOES_HERE>"

current_dir = dirname(realpath(__file__))
TEST_DATA_DIR = join(current_dir, "data")


def iter_test_jsonl_samples():
    with open(join(TEST_DATA_DIR, "sample.jsonl"), "r") as f:
        for line in f.readlines():
            yield json.loads(line)
