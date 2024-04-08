import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.lm.base import BaseLM
from src.utils import auto_import


class DeciLM(BaseLM):

    SYSTEM_PROMPT_TEMPLATE = """
        ### System:
        You are an AI assistant that follows instruction extremely well. Help as much as you can.
        ### User:
        {instruction}
        ### Assistant:
        """

    def __init__(self, model_name="Deci/DeciLM-7B-instruct", temp=0.1, max_length=None, device='cuda',
                 use_bf16=False, load_in_4bit=True):
        """ Embedded from the original page of the model initialization from huggingface.
            Source: https://huggingface.co/Deci/DeciLM-7B-instruct
            Note: Authors by default propose to pass Bits-And-Bytes config with 4Bit Quantization.
        """
        super(DeciLM, self).__init__(name=model_name)

        if use_bf16:
            print("Warning: Experimental mode with bf-16!")

        torch_dtype = torch.bfloat16 if use_bf16 else torch.float32

        # Optional Quantization to 4 bit.
        bnb_config = None
        if load_in_4bit:
            BitsAndBytesConfig = auto_import("transformers.BitsAndBytesConfig", is_class=False)
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch_dtype,
            )

        self.__temp = temp
        self.__device = device
        self.__max_length = 4096 if max_length is None else max_length
        self.__model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
            quantization_config=bnb_config if device != "cpu" else None,
            trust_remote_code=True)
        self.__model.to(device)

        self.__tokenizer = AutoTokenizer.from_pretrained(model_name)

    def ask(self, prompt):
        complete_prompt = self.SYSTEM_PROMPT_TEMPLATE.format(instruction=prompt)
        inputs = self.__tokenizer(complete_prompt,
                                  return_tensors="pt",
                                  add_special_tokens=False)
        inputs.to(self.__device)
        outputs = self.__model.generate(**inputs, max_length=self.__max_length, temperature=self.__temp,
                                        do_sample=True, pad_token_id=50256)
        response = self.__tokenizer.batch_decode(outputs)[0]
        return response if not complete_prompt in response else response[len(complete_prompt):].strip()
