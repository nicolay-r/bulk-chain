from src.llm_base import BaseLM
from src.utils import auto_import


class Replicate(BaseLM):

    LLaMA3_instruct_prompt_template = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

    @staticmethod
    def get_template(max_tokens, temp, top_k=50):
        return {
            "meta/meta-llama-3-8b-instruct": {
                "top_k": top_k,
                "top_p": 0.9,
                "length_penalty": 1,
                "presence_penalty": 1.15,
                "temperature": temp,
                "max_tokens": max_tokens,
                "prompt_template": Replicate.LLaMA3_instruct_prompt_template,
            },
            "meta/meta-llama-3-70b-instruct": {
                "top_k": top_k,
                "min_tokens": 0,
                "presence_penalty": 1.15,
                "frequency_penalty": 0.2,
                "temperature": temp,
                "max_tokens": max_tokens,
                "prompt_template": Replicate.LLaMA3_instruct_prompt_template
            },
            "meta/llama-2-70b-chat": {
                "top_k": top_k,
                "temperature": temp,
                "max_new_tokens": max_tokens,
                "min_new_tokens": -1,
                "prompt_template": Replicate.LLaMA3_instruct_prompt_template
            },
            "meta/meta-llama-3.1-405b-instruct": {
                "top_k": top_k,
                "temperature": temp,
                "max_new_tokens": max_tokens,
                "min_new_tokens": -1,
                "prompt_template": Replicate.LLaMA3_instruct_prompt_template
            }
        }

    def __init__(self, model_name="meta/meta-llama-3-70b-instruct", temp=0.1, max_tokens=512, api_token=None, **kwargs):
        super(Replicate, self).__init__(model_name)
        self.r_model_name = model_name

        all_settings = self.get_template(max_tokens=max_tokens, temp=temp)

        if model_name not in all_settings:
            raise Exception(f"There is no predefined settings for `{model_name}`. Please, Tweak the model first!")

        self.settings = all_settings[model_name]
        client = auto_import("replicate.Client", is_class=False)
        self.client = client(api_token=api_token)

    def ask(self, prompt):

        input_dict = dict(self.settings)

        # Setup prompting message.
        input_dict["prompt"] = prompt

        response = ""
        for event in self.client.stream(self.r_model_name, input=input_dict):
            response += str(event)

        return response