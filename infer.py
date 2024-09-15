import argparse

from os.path import join, basename

from src.csv_service import CsvService
from src.data_service import DataService
from src.json_service import JsonService
from src.llm_service import chat_with_lm
from src.lm.decilm import DeciLM
from src.lm.flan_t5 import FlanT5
from src.lm.gemma import Gemma
from src.lm.llama2 import Llama2
from src.lm.microsoft_phi_2 import MicrosoftPhi2
from src.lm.mistral import Mistral
from src.lm.openai_chatgpt import OpenAIGPT
from src.schema_service import SchemaService
from src.sqlite_provider import SQLiteProvider
from src.utils import find_by_prefix, parse_filepath, handle_table_name, optional_limit_iter


DATA_DIR = "."


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Infer Instruct LLM inference based on CoT schema")
    parser.add_argument('--model', dest='model', type=str, default=None)
    parser.add_argument('--src', dest='src', type=str, default=None)
    parser.add_argument('--schema', dest='schema', type=str, default=None,
                        help="Path to the JSON file that describes schema")
    parser.add_argument('--device', dest='device', type=str, default='cuda')
    parser.add_argument('--csv-sep', dest='csv_sep', type=str, default='\t')
    parser.add_argument('--infer-mode', dest='infer_mode', type=str, default='default')
    parser.add_argument('--to', dest='to', type=str, default=None, choices=["csv", "sqlite"])
    parser.add_argument('--temp', dest='temperature', type=float, default=0.1)
    parser.add_argument('--output', dest='output', type=str, default=None)
    parser.add_argument('--max-length', dest='max_length', type=int, default=None)
    parser.add_argument('--api-token', dest='api_key', type=str, default=None)
    parser.add_argument('--limit', dest='limit', type=int, default=None,
                        help="Limit amount of source texts for prompting.")
    parser.add_argument('--limit-prompt', dest="limit_prompt", type=int, default=None,
                        help="Optional trimming prompt by the specified amount of characters.")
    parser.add_argument('--bf16', dest="use_bf16", action='store_true', default=False,
                        help='Initializing Flan-T5 with torch.bfloat16')
    parser.add_argument('--l4b', dest="load_in_4b", action='store_true', default=False,
                        help='Use 4B Quantization based on Bits-and-Bytes library API')

    args = parser.parse_args()

    # Setup prompt.
    schema = SchemaService(json_data=JsonService.read_data(args.schema))

    if schema is not None:
        print(f"Using schema: {schema.name}")

    transformers_default_cfg = {
        "temp": args.temperature,
        "max_length": args.max_length,
        "token": args.api_key,
        "use_bf16": args.use_bf16,
        "device": args.device
    }

    # List of the Supported models and their API wrappers.
    models_preset = {
        "google/gemma": lambda: Gemma(model_name=llm_model_name, temp=args.temperature, max_length=args.max_length,
                                      token=args.api_key, use_bf16=args.use_bf16, device=args.device),
        "microsoft/phi-2": lambda: MicrosoftPhi2(model_name=llm_model_name, max_length=args.max_length,
                                                 device=args.device, use_bf16=args.use_bf16),
        "mistralai/Mistral": lambda: Mistral(model_name=llm_model_name, temp=args.temperature,
                                             max_length=args.max_length, device=args.device, use_bf16=args.use_bf16),
        "google/flan-t5": lambda: FlanT5(model_name=llm_model_name, temp=args.temperature,
                                         max_length=args.max_length, device=args.device, use_bf16=args.use_bf16),
        "meta-llama/Llama-2": lambda: Llama2(model_name=llm_model_name, temp=args.temperature,
                                             max_length=args.max_length, device=args.device, use_bf16=args.use_bf16),
        "Deci/DeciLM-7B-instruct": lambda: DeciLM(model_name=llm_model_name, temp=args.temperature,
                                                  device=args.device, use_bf16=args.use_bf16, load_in_4bit=args.load_in_4b),
        "openai": lambda: OpenAIGPT(api_key=args.api_token,
                                    model_name=llm_model_name, temp=args.temperature, max_tokens=args.max_length),
    }

    input_providers = {
        None: lambda _: chat_with_lm(llm, chain=schema.chain, model_name=llm_model_name),
        "csv": lambda filepath: CsvService.read(target=filepath, row_id_key="uid", delimiter=args.csv_sep,
                                                as_dict=True, skip_header=True, escapechar=args.csv_escape_char)
    }

    infer_modes = {
        "default": lambda prompt: llm.ask(prompt[:args.limit_prompt] if args.limit_prompt is not None else prompt)
    }

    def optional_update_data_records(c, data):
        assert (isinstance(c, str))

        if c in schema.p2r:
            data[c] = DataService.get_prompt_text(prompt=data[c]["prompt"], data_dict=data)
        if c in schema.r2p:
            p_column = schema.r2p[c]
            # This instruction takes a lot of time in a non-batching mode.
            data[c] = infer_modes[args.infer_mode](data[p_column])

        return data[c]

    output_providers = {
        "sqlite": lambda filepath, table_name: SQLiteProvider.write_auto(
            data_it=queries_it, target=filepath,
            data2col_func=optional_update_data_records,
            table_name=handle_table_name(table_name if table_name is not None else "contents"),
            id_column_name="uid")
    }

    # Initialize LLM model.
    llm_model_type = args.model.split(':')[0]
    llm_model_name = args.model.split(':')[-1]
    llm = find_by_prefix(d=models_preset, key=args.model.split(':')[0])()

    # Input extension type defines the provider.
    src_filepath, src_ext, src_meta = parse_filepath(args.src)
    queries_it = map(lambda data: data.update(schema.cot_args) or data, input_providers[src_ext](src_filepath))

    # If this is not a chat mode, then we optionally wrap into limiter.
    if src_ext is not None:
        queries_it = optional_limit_iter(it_data=queries_it, limit=args.limit)

    # Setup output.
    args.output = args.output.format(model=llm.name()) if args.output is not None else args.output
    tgt_filepath, tgt_ext, tgt_meta = parse_filepath(args.output, default_ext=args.to)

    # We may still not decided the result extension so then assign the default one.
    # In the case when both --to and --output parameters were not defined.
    tgt_ext = "sqlite" if tgt_ext is None else tgt_ext

    actual_target = "".join(["_".join([join(DATA_DIR, basename(src_filepath)), llm.name(), schema.name]), f".{tgt_ext}"]) \
        if tgt_filepath is None else tgt_filepath

    # Provide output.
    output_providers[tgt_ext](actual_target, tgt_meta)
