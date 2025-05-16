class BaseLM(object):

    def __init__(self, **kwargs):
        pass

    def ask(self, content):
        """ Assumes to return str.
        """
        raise NotImplemented()

    def ask_stream(self, content):
        """ Assumes to return generator.
        """
        raise NotImplemented()

    async def ask_async(self, prompt):
        """ Assumes to return co-routine.
        """
        raise NotImplemented()

    async def ask_stream_async(self, batch):
        """ Assumes to return AsyncGenerator.
        """
        raise NotImplemented()
