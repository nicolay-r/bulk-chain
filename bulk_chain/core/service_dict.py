class DictionaryService:

    @staticmethod
    def custom_update(src_dict, other_dict):
        for k, v in other_dict.items():
            if k in src_dict:
                raise Exception(f"The key `{k}` is already defined in both dicts with values: "
                                f"`{src_dict[k]}` (src) and `{v}` (other)")
            src_dict[k] = v
        return src_dict
