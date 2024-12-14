import unittest

from bulk_chain.core.service_json import JsonService
from bulk_chain.core.service_schema import SchemaService
from bulk_chain.infer import iter_content
from ext.replicate import Replicate


class TestAPI(unittest.TestCase):

    def it_data(self, n):
        for i in range(n):
            yield {"ind": i, "text": "X invent sanctions against Y", "entity": "X"}

    def test(self):
        data_it = iter_content(input_dicts_it=self.it_data(20),
                               llm=Replicate(model_name="meta/meta-llama-3-8b-instruct", api_token="<API-TOKEN>"),
                               cache_target="out.sqlite:content",
                               schema=SchemaService(json_data=JsonService.read("../ext/schema/default.json")),
                               id_column_name="ind")

        for data in data_it:
            print(data)


if __name__ == '__main__':
    unittest.main()
