import logging
import time

from bulk_chain.core.utils import format_model_name


class BaseLM(object):

    def __init__(self, name, attempts=None, delay_sec=1, enable_log=True):
        self.__name = name
        self.__attempts = 1 if attempts is None else attempts
        self.__delay_sec = delay_sec

        if enable_log:
            self.__logger = logging.getLogger(__name__)
            logging.basicConfig(level=logging.INFO)

    def ask_safe(self, prompt):

        for i in range(self.__attempts):
            try:
                response = self.ask(prompt)
                return response
            except:
                if self.__logger is not None:
                    self.__logger.info("Unable to infer the result. Try {} out of {}.".format(i, self.__attempts))
                time.sleep(self.__delay_sec)

        raise Exception("Can't infer")

    def ask(self, prompt):
        raise NotImplemented()

    def name(self):
        return format_model_name(self.__name)
