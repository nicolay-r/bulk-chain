import json


class JsonService(object):

    @staticmethod
    def read_data(src):
        assert (isinstance(src, str))
        with open(src, "r") as f:
            return json.load(f)

    @staticmethod
    def pretty(src, indent):
        return json.dumps(src, indent=2)
