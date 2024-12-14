import unittest

from bulk_chain.infer import iter_content
from ext.replicate import Replicate


class TestAPI(unittest.TestCase):

    def it_data(self, n):
        for i in range(n):
            yield {"ind": i, "text": "X invent sanctions against Y", "entity": "X"}

    def test(self):
        data_it = iter_content(input_dicts_it=self.it_data(20),
                               llm=Replicate(model_name="meta/meta-llama-3-8b-instruct",
                                             api_token="<API-TOKEN>"),
                               schema="../ext/schema/default.json",
                               # Cache-related extra parameters.
                               cache_target="out.sqlite:content",
                               id_column_name="ind")

        for data in data_it:
            print(data)


if __name__ == '__main__':
    unittest.main()
