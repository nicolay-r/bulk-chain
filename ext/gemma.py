import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from bulk_chain.core.llm_base import BaseLM


class Gemma(BaseLM):

    def __init__(self, model_name="google/gemma-7b-it", temp=0.1, device='cuda',
                 max_length=None, api_token=None, use_bf16=False, **kwargs):
        super(Gemma, self).__init__(name=model_name, **kwargs)
        self.__device = device
        self.__max_length = 1024 if max_length is None else max_length
        self.__model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.bfloat16 if use_bf16 else "auto", token=api_token)
        self.__model.to(device)
        self.__tokenizer = AutoTokenizer.from_pretrained(model_name, token=api_token)
        self.__temp = temp

    def ask(self, prompt):
        inputs = self.__tokenizer(prompt, return_tensors="pt")
        inputs.to(self.__device)
        outputs = self.__model.generate(**inputs, max_length=self.__max_length, temperature=self.__temp,
                                        do_sample=True, pad_token_id=50256)
        return self.__tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
