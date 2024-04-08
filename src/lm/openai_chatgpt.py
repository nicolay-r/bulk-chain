from src.lm.base import BaseLM
from src.utils import auto_import


class OpenAIGPT(BaseLM):

    def __init__(self, api_key, model_name="gpt-4-1106-preview", temp=0.1, max_tokens=None, assistant_prompt=None,
                 freq_penalty=0.0, kwargs=None):
        assert(isinstance(assistant_prompt, str) or assistant_prompt is None)
        super(OpenAIGPT, self).__init__(name=model_name)

        # dynamic import of the OpenAI library.
        OpenAI = auto_import("openai._client.OpenAI", is_class=False)

        self.__client = OpenAI(api_key=api_key)
        self.__max_tokens = 256 if max_tokens is None else max_tokens
        self.__temperature = temp
        self.__model_name = model_name
        self.__assistant_prompt = assistant_prompt if assistant_prompt is not None else None
        self.__freq_penalty = freq_penalty
        self.__kwargs = {} if kwargs is None else kwargs

    def ask(self, prompt):

        message = [
            {"role": "assistant", "content": self.__assistant_prompt},
            {"role": "user", "content": prompt}
        ]

        response = self.__client.chat.completions.create(
            model=self.__model_name,
            messages=message,
            temperature=self.__temperature,
            max_tokens=self.__max_tokens,
            frequency_penalty=self.__freq_penalty,
            **self.__kwargs
        )
        return response.choices[0].message.content
