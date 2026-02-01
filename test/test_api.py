import unittest
from os.path import join

from bulk_chain.api import iter_content
from utils import current_dir, default_remote_llm


class TestAPI(unittest.TestCase):

    llm = default_remote_llm()

    @staticmethod
    def it_data(n):
        for i in range(n):
            yield {"ind": i, "text": "X invent sanctions against Y", "entity": "X"}

    def test_single(self):
        data_it = iter_content(input_dicts_it=self.it_data(20),
                               llm=self.llm,
                               batch_size=1,
                               schema=join(current_dir, "schema/default.json"))

        for data in data_it:
            print(data)

    def test_single_stream(self):
        """ Returns individual chunks.
        """
        chunk_it = iter_content(input_dicts_it=self.it_data(20),
                                llm=self.llm,
                                batch_size=1,
                                stream=True,
                                schema=join(current_dir, "schema/default.json"))

        for data in chunk_it:
            print(data)

    def test_batch_async(self):
        """ Return batches that passed async at the Replicate.
        """
        batch_it = iter_content(input_dicts_it=self.it_data(20),
                                llm=self.llm,
                                batch_size=5,
                                async_mode=True,
                                schema=join(current_dir, "schema/default.json"))

        for batch in batch_it:
            for item in batch:
                print(item)

    def test_batch_stream_async(self):
        chunk_it = iter_content(input_dicts_it=self.it_data(20),
                                llm=self.llm,
                                batch_size=5,
                                stream=True,
                                async_mode=True,
                                schema=join(current_dir, "schema/default.json"))

        for chunk_info in chunk_it:
            print(chunk_info)


if __name__ == '__main__':
    unittest.main()
