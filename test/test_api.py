import unittest
from os.path import join

from bulk_chain.api import iter_content, CWD
from bulk_chain.core.utils import dynamic_init
from bulk_chain.infer import iter_content_cached
from utils import current_dir, API_TOKEN


class TestAPI(unittest.TestCase):

    llm = dynamic_init(class_dir=join(CWD, ".."),
                       class_filepath="providers/replicate_104.py",
                       class_name="Replicate")(api_token=API_TOKEN,
                                               model_name="deepseek-ai/deepseek-r1")

    def it_data(self, n):
        for i in range(n):
            yield {"ind": i, "text": "X invent sanctions against Y", "entity": "X"}

    def test_iter_cached(self):
        data_it = iter_content_cached(input_dicts_it=self.it_data(20),
                                      llm=self.llm,
                                      batch_size=1,
                                      schema=join(current_dir, "schema/default.json"),
                                      # Cache-related extra parameters.
                                      cache_target="out.sqlite:content",
                                      id_column_name="ind")

        for data in data_it:
            print(data)

    def test_iter(self):
        data_it = iter_content(input_dicts_it=self.it_data(20),
                               llm=self.llm,
                               batch_size=1,
                               return_batch=True,
                               handle_missed_value_func=lambda *_: None,
                               schema=join(current_dir, "schema/default.json"))

        for data in data_it:
            print(data)


if __name__ == '__main__':
    unittest.main()
