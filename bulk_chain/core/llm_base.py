import logging
import time

from bulk_chain.core.utils import format_model_name


class BaseLM(object):

    def __init__(self, name=None, attempts=None, delay_sec=1, enable_log=True,
                 support_batching=False, **kwargs):

        self.__name = name
        self.__attempts = 1 if attempts is None else attempts
        self.__delay_sec = delay_sec
        self.__support_batching = support_batching

        if enable_log:
            self.__logger = logging.getLogger(__name__)
            logging.basicConfig(level=logging.INFO)

    def ask_core(self, batch):

        for i in range(self.__attempts):
            try:
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

            except Exception as e:
                if self.__logger is not None:
                    self.__logger.info("Unable to infer the result. Try {} out of {}.".format(i, self.__attempts))
                    self.__logger.info(e)
                time.sleep(self.__delay_sec)

        raise Exception("Can't infer")

    def ask(self, content):
        raise NotImplemented()

    def name(self):
        return format_model_name(self.__name)
