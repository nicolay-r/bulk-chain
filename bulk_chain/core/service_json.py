import json


class JsonService(object):

    @staticmethod
    def read(src):
        assert (isinstance(src, str))
        with open(src, "r") as f:
            return json.load(f)