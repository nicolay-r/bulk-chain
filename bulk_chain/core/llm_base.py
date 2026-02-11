class BaseLM(object):

    def __init__(self, **kwargs):
        pass

    def ask(self, prompt):
        """ Assumes to return str.
        """
        raise NotImplemented()

    def ask_batch(self, batch):
        """ Assumes to return generator.
        """
        raise NotImplemented()

    def ask_stream(self, prompt):
        """ Assumes to return generator.
        """
        raise NotImplemented()

    async def ask_async(self, prompt):
        """ Accepts single prompt and returns co-routine.
        """
        raise NotImplemented()

    async def ask_stream_async(self, prompt):
        """ Accepts single prompt and returns AsyncGenerator.
        """
        raise NotImplemented()

    async def ask_batch_async(self, batch):
        """ Accepts batch of prompts and returns co-routine.
        """
        raise NotImplemented()

    async def ask_stream_batch_async(self, batch):
        """ Accepts batch of prompts and returns AsyncGenerator.
        """
        raise NotImplemented()