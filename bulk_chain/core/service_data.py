from bulk_chain.core.utils import iter_params


class DataService(object):

    @staticmethod
    def __compose_prompt_text(prompt, data_dict, field_names):
        assert (isinstance(data_dict, dict))
        fmt_d = {col_name: data_dict[col_name] for col_name in field_names}

        # Guarantee that items has correct type.
        for k, v in fmt_d.items():
            if not isinstance(v, str):
                Exception("'{k}' parameter is expected to be string, but received '{v}'")

        return prompt.format(**fmt_d)

    @staticmethod
    def __default_none_handler(col_name):
        raise Exception(f"Can't compose prompt! Value for `{col_name}` is undefined!")

    @staticmethod
    def get_prompt_text(prompt, data_dict, parse_fields_func=iter_params, handle_missed_func=None):
        field_names = list(parse_fields_func(prompt))

        handle_missed_func = DataService.__default_none_handler if not handle_missed_func else handle_missed_func

        for col_name in field_names:
            if col_name not in data_dict:
                data_dict[col_name] = handle_missed_func(col_name)

        return DataService.__compose_prompt_text(prompt=prompt, data_dict=data_dict, field_names=field_names)

    @staticmethod
    def limit_prompts(prompts_list, limit=None):
        return [p[:limit] if limit is not None else p for p in prompts_list]
