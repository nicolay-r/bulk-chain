import json


class JsonService(object):

    @staticmethod
    def read_data(src):
        assert (isinstance(src, str))
        with open(src, "r") as f:
            return json.load(f)

    @staticmethod
    def read_lines(src, row_id_key=None):
        assert (isinstance(src, str))
        with open(src, "r") as f:
            for line_ind, line in enumerate(f.readlines()):
                content = json.loads(line)
                if row_id_key is not None:
                    content[row_id_key] = line_ind
                yield content

    @staticmethod
    def write_lines(target, data_it):
        with open(target, "w") as f:
            for item in data_it:
                f.write(f"{json.dumps(item, ensure_ascii=False)}\n")