import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from bulk_chain.core.llm_base import BaseLM


class Llama2(BaseLM):

    def __init__(self, model_name, temp=0.1, device='cuda', max_length=None, token=None, use_bf16=False):
        super(Llama2, self).__init__(name=model_name)

        if use_bf16:
            print("Warning: Experimental mode with bf-16!")

        self.__device = device
        self.__max_length = 1024 if max_length is None else max_length
        self.__model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.bfloat16 if use_bf16 else "auto", token=token)
        self.__model.to(device)
        self.__tokenizer = AutoTokenizer.from_pretrained(
            model_name, torch_dtype=torch.bfloat16 if use_bf16 else "auto", token=token)
        self.__temp = temp

    def ask(self, prompt):
        inputs = self.__tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
        inputs.to(self.__device)
        outputs = self.__model.generate(**inputs, max_length=self.__max_length, temperature=self.__temp,
                                        do_sample=True, pad_token_id=50256)
        return self.__tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
