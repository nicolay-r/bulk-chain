from bulk_chain.core.service_schema import SchemaService


class DataService(object):

    @staticmethod
    def __compose_prompt_text(prompt, data_dict, field_names):
        assert (isinstance(data_dict, dict))
        fmt_d = {col_name: data_dict[col_name] for col_name in field_names}

        # Guarantee that items has correct type.
        for k, v in fmt_d.items():
            if not isinstance(v, str):
                Exception("'{k}' parameter is expected to be string, but received '{v}'")

        return prompt.format(**fmt_d) if len(fmt_d) > 0 else prompt

    @staticmethod
    def __get_prompt_text(prompt, data_dict, parse_fields_func, handle_missed_func=None):
        field_names = list(parse_fields_func(prompt))

        for col_name in field_names:
            if col_name not in data_dict:
                data_dict[col_name] = handle_missed_func(col_name)

        return DataService.__compose_prompt_text(prompt=prompt, data_dict=data_dict, field_names=field_names)

    @staticmethod
    def resolve_schema_entry(schema_entry, data_dict, parse_fields_func, handle_missed_func=None):
        resolved = {}
        for field_name, field_value in SchemaService.llm_fields(schema_entry).items():
            if isinstance(field_value, str):
                resolved[field_name] = DataService.__get_prompt_text(
                    prompt=field_value,
                    data_dict=data_dict,
                    parse_fields_func=parse_fields_func,
                    handle_missed_func=handle_missed_func)
            elif isinstance(field_value, list):
                resolved[field_name] = [
                    DataService.__get_prompt_text(
                        prompt=item,
                        data_dict=data_dict,
                        parse_fields_func=parse_fields_func,
                        handle_missed_func=handle_missed_func)
                    if isinstance(item, str) else item
                    for item in field_value
                ]
            else:
                resolved[field_name] = field_value
        return resolved

    @staticmethod
    def limit_prompts(prompts_list, limit=None):
        if limit is None:
            return prompts_list

        limited = []
        for item in prompts_list:
            if isinstance(item, dict):
                entry = dict(item)
                if "prompt" in entry:
                    entry["prompt"] = entry["prompt"][:limit]
                limited.append(entry)
            else:
                limited.append(item[:limit])
        return limited

    @staticmethod
    def llm_call_args(item):
        if isinstance(item, dict):
            return item["prompt"], {k: v for k, v in item.items() if k != "prompt"}
        return item, {}

    @staticmethod
    def call_llm(handler, item):
        prompt, kwargs = DataService.llm_call_args(item)
        return handler(prompt, **kwargs)
