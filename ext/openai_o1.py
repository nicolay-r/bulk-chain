import logging

from openai import OpenAI
from bulk_chain.core.llm_base import BaseLM

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class OpenAIGPT(BaseLM):
    """ O1-version does not support temperature parameter.
        O1 exploits `max_completion_tokens` parameter.
            - if completion tokens won't be enough then the output might be EMPTY.
    """

    def __init__(self, api_key, model_name="o1-preview-2024-09-12", assistant_prompt=None,
                 max_completion_tokens=None, freq_penalty=0.0, attempts=None,
                 suppress_httpx_log=True, **kwargs):
        assert (isinstance(assistant_prompt, str) or assistant_prompt is None)
        super(OpenAIGPT, self).__init__(name=model_name, attempts=attempts, **kwargs)

        if max_completion_tokens is not None:
            logger.info("if completion tokens won't be enough then the output might be EMPTY.")

        # dynamic import of the OpenAI library.
        self.__client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")
        self.__max_completion_tokens = max_completion_tokens
        self.__model_name = model_name
        self.__assistant_prompt = assistant_prompt if assistant_prompt is not None else None
        self.__freq_penalty = freq_penalty
        self.__kwargs = {} if kwargs is None else kwargs

        if "delimiter" in self.__kwargs:
            del self.__kwargs["delimiter"]

        if suppress_httpx_log:
            httpx_logger = logging.getLogger("httpx")
            httpx_logger.setLevel(logging.WARNING)

    def ask(self, prompt):

        def __msg_content():
            if self.__assistant_prompt is not None:
                yield {"role": "assistant", "content": self.__assistant_prompt}
            yield {"role": "user", "content": prompt}

        response = self.__client.chat.completions.create(
            model=self.__model_name,
            messages=list(__msg_content()),
            max_completion_tokens=self.__max_completion_tokens,
            frequency_penalty=self.__freq_penalty,
            **self.__kwargs
        )

        return response.choices[0].message.content