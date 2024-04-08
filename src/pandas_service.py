from tqdm import tqdm


class PandasService(object):

    @staticmethod
    def iter_rows_as_dict(df, row_id_key=None):
        assert(isinstance(row_id_key, str) or row_id_key is None)
        for row_id, data in tqdm(df.iterrows(), total=len(df)):
            data_dict = data.to_dict()
            if row_id is not None:
                data_dict.update({row_id_key: row_id})
            yield data_dict
