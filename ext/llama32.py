import torch
from transformers import pipeline

from bulk_chain.core.llm_base import BaseLM


class Llama32(BaseLM):

    def __init__(self, model_name="meta-llama/Llama-3.2-3B-Instruct", api_token=None,
                 temp=0.1, device='cuda', max_length=256, use_bf16=False, **kwargs):
        super(Llama32, self).__init__(name=model_name, **kwargs)

        if use_bf16:
            print("Warning: Experimental mode with bf-16!")

        self.__device = device
        self.__max_length = 1024 if max_length is None else max_length
        self.__pipe = pipeline(
            "text-generation",
            model=model_name,
            torch_dtype=torch.bfloat16 if use_bf16 else "auto",
            device_map="auto",
            temperature=temp,
            token=api_token
        )

    def ask(self, prompt):
        outputs = self.__pipe(
            [{"role": "user", "content": prompt}],
            max_new_tokens=self.__max_length,
        )
        return (outputs[0]["generated_text"][-1]) 
