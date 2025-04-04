import unittest
from os.path import join

from tqdm import tqdm

from bulk_chain.api import CWD, iter_content
from bulk_chain.core.utils import dynamic_init
from utils import iter_test_jsonl_samples


class TestProviderBatching(unittest.TestCase):

    llm = dynamic_init(class_dir=join(CWD),
                       class_filepath="providers/transformers_flan_t5.py",
                       class_name="FlanT5")(model_name="nicolay-r/flan-t5-tsa-thor-base",
                                            max_new_tokens=128)

    def test_iter(self):
        input_dicts_it = iter_test_jsonl_samples()
        data_it = iter_content(input_dicts_it=input_dicts_it,
                               llm=self.llm,
                               batch_size=10,
                               return_batch=False,
                               handle_missed_value_func=lambda *_: None,
                               schema="schema/thor_cot_schema.json")

        for item in tqdm(data_it):
            print(item)


if __name__ == '__main__':
    unittest.main()
