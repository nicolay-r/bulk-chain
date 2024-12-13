from bulk_chain.core.service_json import JsonService
from bulk_chain.core.service_schema import SchemaService
from bulk_chain.infer import iter_content
from ext.replicate import Replicate


input_dict = {
    "text": "X invent sanctions against Y",
    "entity": "X"
}


data_it = iter_content(input_dicts_it=[input_dict],
                       llm=Replicate(model_name="meta/meta-llama-3-8b-instruct",
                                     api_token="<KEY>"),
                       cache_target="out.sqlite:content",
                       schema=SchemaService(json_data=JsonService.read("../ext/schema/default.json")),
                       id_column_name="text")

for data in data_it:
    print(data)