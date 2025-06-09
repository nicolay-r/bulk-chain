import json
from os.path import join, dirname, realpath

from bulk_chain.core.utils import dynamic_init

current_dir = dirname(realpath(__file__))
TEST_DATA_DIR = join(current_dir, "data")


def default_remote_llm():
    return dynamic_init(class_filepath="providers/replicate_104.py")(
        api_token="TOKEN_GOES_HERE",
        model_name="meta/meta-llama-3-8b-instruct",
        stream=True)


def iter_test_jsonl_samples():
    with open(join(TEST_DATA_DIR, "sample.jsonl"), "r") as f:
        for line in f.readlines():
            yield json.loads(line)