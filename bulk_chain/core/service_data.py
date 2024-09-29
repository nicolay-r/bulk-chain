from bulk_chain.core.utils import iter_params


class DataService(object):

    @staticmethod
    def compose_prompt_text(prompt, data_dict, field_names):
        assert(isinstance(data_dict, dict))
        fmt_d = {col_name: data_dict[col_name] for col_name in field_names}

        # Guarantee that items has correct type.
        for k, v in fmt_d.items():
            if not isinstance(v, str):
                Exception("'{k}' parameter is expected to be string, but received '{v}'")

        return prompt.format(**fmt_d)

    @staticmethod
    def get_prompt_text(prompt, data_dict, parse_fields_func=iter_params):
        field_names = list(parse_fields_func(prompt))
        return DataService.compose_prompt_text(
            prompt=prompt, data_dict=data_dict, field_names=field_names)
