import json

import argparse
import logging
import sys

from source_iter.service_jsonl import JsonlService

from bulk_chain.api import init_llm
from bulk_chain.core.service_args import CmdArgsService
from bulk_chain.core.service_json import JsonService
from bulk_chain.core.service_llm import chat_with_lm
from bulk_chain.core.service_schema import SchemaService
from bulk_chain.core.utils import parse_filepath

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def iter_from_json(filepath):
    with open(filepath, "r") as f:
        content = json.load(f)
        for key, value in content.items():
            yield key, value


def iter_from_text_file(filepath):
    with open(filepath, "r") as f:
        yield filepath.split('.')[0], f.read()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="LLM demo usage based on CoT schema")
    parser.add_argument('--adapter', dest='adapter', type=str, default=None)
    parser.add_argument('--attempts', dest='attempts', type=int, default=None)
    parser.add_argument('--src', dest='src', type=str, nargs="*", default=None)
    parser.add_argument('--schema', dest='schema', type=str, default=None,
                        help="Path to the JSON file that describes schema")
    parser.add_argument('--limit-prompt', dest="limit_prompt", type=int, default=None,
                        help="Optional trimming prompt by the specified amount of characters.")

    # Extract native arguments.
    native_args = CmdArgsService.extract_native_args(sys.argv, end_prefix="%%")
    args = parser.parse_args(args=native_args[1:])

    # Extract model-related arguments and Initialize Large Language Model.
    model_args = CmdArgsService.find_grouped_args(lst=sys.argv, starts_with="%%m", end_prefix="%%")
    model_args_dict = CmdArgsService.args_to_dict(model_args) | {"attempts": args.attempts}
    llm, llm_model_name = init_llm(adapter=args.adapter, **model_args_dict)

    # Setup schema.
    schema = SchemaService(json_data=JsonService.read(args.schema))
    schema_name = schema.src.get("name", None)
    if schema is not None:
        logger.info(f"Using schema: {schema_name}")

    output_providers = {
        "jsonl": lambda filepath, data_it, header:
            JsonlService.write(target=filepath,
                               data_it=map(lambda item: {key: item[i] for i, key in enumerate(header)}, data_it))
    }

    input_file_handlers = {
        "json": lambda filepath: iter_from_json(filepath),
        "txt": lambda filepath: iter_from_text_file(filepath)
    }

    # Input extension type defines the provider.
    if args.src is None:
        args.src = []
    if isinstance(args.src, str):
        args.src = [args.src]
    sources = [parse_filepath(s) for s in args.src]

    preset_dict = {}
    for fp, ext, _ in sources:
        for key, value in input_file_handlers[ext](fp):
            if key in preset_dict:
                raise Exception(f"While at handling {fp}: Key {key} is already registered!")
            preset_dict[key] = value

    # Launch Demo.
    chat_with_lm(llm, preset_dict=preset_dict, schema=schema, model_name=llm_model_name)
