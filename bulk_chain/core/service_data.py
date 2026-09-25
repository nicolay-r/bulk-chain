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
    def __ensure_fields(field_names, data_dict, handle_missed_func):
        for col_name in field_names:
            if col_name not in data_dict:
                data_dict[col_name] = handle_missed_func(col_name)

    @staticmethod
    def __get_value(field_value, data_dict, parse_fields_func, handle_missed_func=None):

        if isinstance(field_value, list):
            return [
                DataService.__get_value(
                    field_value=item,
                    data_dict=data_dict,
                    parse_fields_func=parse_fields_func,
                    handle_missed_func=handle_missed_func,
                )
                for item in field_value
            ]

        if isinstance(field_value, tuple):
            if len(field_value) != 2 or not isinstance(field_value[0], str):
                raise ValueError(f"Typed field must be (prompt, type), got {field_value!r}")
            prompt, expected_type = field_value
            field_names = list(parse_fields_func(prompt))
            if len(field_names) != 1:
                raise ValueError(f"Typed field {prompt!r} must name exactly one column")
            DataService.__ensure_fields(field_names, data_dict, handle_missed_func)
            value = data_dict[field_names[0]]
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"{field_names[0]!r} is {type(value).__name__}, expected {expected_type}"
                )

            return value

        if isinstance(field_value, str):
            field_names = list(parse_fields_func(field_value))
            DataService.__ensure_fields(field_names, data_dict, handle_missed_func)
            return DataService.__compose_prompt_text(
                prompt=field_value, data_dict=data_dict, field_names=field_names)
                
        return field_value

    @staticmethod
    def resolve_schema_entry(schema_entry, **kwargs):
        return {
            field_name: DataService.__get_value(field_value=field_value, **kwargs)
            for field_name, field_value in SchemaService.llm_fields(schema_entry).items()
        }

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
