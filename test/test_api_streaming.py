import unittest

from bulk_chain.api import iter_content
from utils import iter_test_jsonl_samples, DEFAULT_REMOTE_LLM


class TestAPI_Streaming(unittest.TestCase):

    def test_content_iter_mode(self):

        input_dicts_it = iter_test_jsonl_samples()
        data_it = iter_content(input_dicts_it=input_dicts_it,
                               llm=DEFAULT_REMOTE_LLM,
                               batch_size=1,
                               infer_mode="single_stream",
                               return_mode="chunk",
                               attempts=2,
                               schema="schema/thor_cot_schema.json")

        for ind_in_batch, col, item in data_it:
            print("\t".join([str(ind_in_batch), str(col), item]))
