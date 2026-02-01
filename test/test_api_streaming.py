import unittest

from bulk_chain.api import iter_content
from utils import iter_test_jsonl_samples, default_remote_llm


class TestAPI_Streaming(unittest.TestCase):

    def test_content_iter_mode(self):

        input_dicts_it = iter_test_jsonl_samples()
        data_it = iter_content(input_dicts_it=input_dicts_it,
                               llm=default_remote_llm(),
                               batch_size=1,
                               stream=True,
                               attempts=2,
                               schema="schema/thor_cot_schema.json")

        for ind_in_batch, col, item in data_it:
            print("\t".join([str(ind_in_batch), str(col), item]))
