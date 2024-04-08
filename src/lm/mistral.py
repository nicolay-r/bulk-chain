import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.lm.base import BaseLM


class Mistral(BaseLM):

    def __init__(self, model_name="mistralai/Mistral-7B-Instruct-v0.1", temp=0.1, device='cuda', max_length=None,
                 use_bf16=False):
        assert(isinstance(max_length, int) or max_length is None)
        super(Mistral, self).__init__(name=model_name)

        if use_bf16:
            print("Warning: Experimental mode with bf-16!")

        self.__device = device
        self.__max_length = 512 if max_length is None else max_length
        self.__check_params()
        self.__model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.bfloat16 if use_bf16 else "auto")
        self.__model.to(device)
        self.__tokenizer = AutoTokenizer.from_pretrained(
            model_name, torch_dtype=torch.bfloat16 if use_bf16 else "auto")
        self.__temp = temp

    def __check_params(self):
        # https://huggingface.co/mistralai/Mistral-7B-v0.1/discussions/4#6514a8c5be453924e06026f5
        assert(0 < self.__max_length < 8192)

    def ask(self, prompt):
        inputs = self.__tokenizer(f"""<s>[INST]{prompt}[/INST]""", return_tensors="pt", add_special_tokens=False)
        inputs.to(self.__device)
        outputs = self.__model.generate(**inputs, max_length=self.__max_length, temperature=self.__temp,
                                        do_sample=True, pad_token_id=50256)
        response = self.__tokenizer.batch_decode(outputs)[0]
        parts = response.split("[/INST]")
        return "".join(parts[1:]) if len(parts) > 1 else ""
