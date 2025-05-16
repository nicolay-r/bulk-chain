import unittest
from os.path import join

from bulk_chain.api import iter_content
from utils import current_dir, DEFAULT_REMOTE_LLM


class TestAPI(unittest.TestCase):


    @staticmethod
    def it_data(n):
        for i in range(n):
            yield {"ind": i, "text": "X invent sanctions against Y", "entity": "X"}

    def test_single(self):
        data_it = iter_content(input_dicts_it=self.it_data(20),
                               llm=DEFAULT_REMOTE_LLM,
                               batch_size=1,
                               infer_mode="single",
                               return_mode="batch",
                               schema=join(current_dir, "schema/default.json"))

        for data in data_it:
            print(data)

    def test_single_stream(self):
        """ Returns individual chunks.
        """
        data_it = iter_content(input_dicts_it=self.it_data(20),
                               llm=DEFAULT_REMOTE_LLM,
                               batch_size=1,
                               infer_mode="single_stream",
                               return_mode="chunk",
                               schema=join(current_dir, "schema/default.json"))

        for data in data_it:
            print(data)

    def test_batch_async(self):
        """ Return batches that passed async at the Replicate.
        """
        data_it = iter_content(input_dicts_it=self.it_data(20),
                               llm=DEFAULT_REMOTE_LLM,
                               batch_size=5,
                               infer_mode="batch_async",
                               return_mode="batch",
                               schema=join(current_dir, "schema/default.json"))

        for batch in data_it:
            for item in batch:
                print(item)

    def test_batch_stream_async(self):
        data_it = iter_content(input_dicts_it=self.it_data(20),
                               llm=DEFAULT_REMOTE_LLM,
                               batch_size=5,
                               infer_mode="batch_stream_async",
                               return_mode="chunk",
                               schema=join(current_dir, "schema/default.json"))

        for chunk_info in data_it:
            print(chunk_info)


if __name__ == '__main__':
    unittest.main()
