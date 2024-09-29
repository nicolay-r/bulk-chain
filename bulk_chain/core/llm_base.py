from bulk_chain.core.utils import format_model_name


class BaseLM(object):

    def __init__(self, name):
        self.__name = name

    def ask(self, prompt):
        raise NotImplemented()

    def name(self):
        return format_model_name(self.__name)