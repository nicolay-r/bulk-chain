class BaseLM(object):

    def __init__(self, **kwargs):
        pass

    def ask(self, content):
        raise NotImplemented()

    def ask_stream(self, content):
        raise NotImplemented()

    async def ask_async(self, prompt):
        raise NotImplemented()

    async def ask_stream_async(self, prompt):
        raise NotImplemented()
