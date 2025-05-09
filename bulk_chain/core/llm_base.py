class BaseLM(object):

    def __init__(self, support_batching=False, **kwargs):
        assert (support_batching, bool)
        self.__support_batching = support_batching

    def ask_core(self, batch):
        if self.__support_batching:
            # Launch in batch mode.
            content = batch
        else:
            # Launch in non-batch mode.
            assert len(batch) == 1, "The LM does not support batching," \
                                    f" while size of the content is {len(batch)} which is not equal 1. " \
                                    f"Please enable batch-supporting or set required inference settings."
            content = batch[0]

        response = self.ask(content)

        # Wrapping into batch the response in the case of non-batching mode.
        return response if self.__support_batching else [response]

    def ask(self, content):
        raise NotImplemented()
