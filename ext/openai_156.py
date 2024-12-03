# This code has been tested under openai==1.56.0

import logging

from openai import OpenAI
from bulk_chain.core.llm_base import BaseLM


class OpenAIGPT(BaseLM):

    def __init__(self, api_key, model_name="gpt-4-1106-preview", temp=0.1, max_tokens=None, assistant_prompt=None,
                 freq_penalty=0.0, attempts=None, suppress_httpx_log=True, **kwargs):
        assert (isinstance(assistant_prompt, str) or assistant_prompt is None)
        super(OpenAIGPT, self).__init__(name=model_name, attempts=attempts, **kwargs)

        # dynamic import of the OpenAI library.
        self.__client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")
        self.__max_tokens = 256 if max_tokens is None else max_tokens
        self.__temperature = temp
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

        message = list(__msg_content())

        response = self.__client.chat.completions.create(
            model=self.__model_name,
            messages=message,
            temperature=self.__temperature,
            max_tokens=self.__max_tokens,
            frequency_penalty=self.__freq_penalty,
            **self.__kwargs
        )

        return response.choices[0].message.content
