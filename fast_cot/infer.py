import argparse
import logging
import os
import sys

from tqdm import tqdm

from os.path import join, basename

from fast_cot.core.provider_sqlite import SQLiteProvider
from fast_cot.core.service_args import CmdArgsService
from fast_cot.core.service_csv import CsvService
from fast_cot.core.service_data import DataService
from fast_cot.core.service_json import JsonService
from fast_cot.core.service_llm import chat_with_lm
from fast_cot.core.service_schema import SchemaService
from fast_cot.core.utils import find_by_prefix, parse_filepath, handle_table_name, optional_limit_iter, auto_import, \
    dynamic_init

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


CWD = os.getcwd()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Infer Instruct LLM inference based on CoT schema")
    parser.add_argument('--adapter', dest='adapter', type=str, default=None)
    parser.add_argument('--src', dest='src', type=str, default=None)
    parser.add_argument('--schema', dest='schema', type=str, default=None,
                        help="Path to the JSON file that describes schema")
    parser.add_argument('--csv-sep', dest='csv_sep', type=str, default='\t')
    parser.add_argument('--csv-escape-char', dest='csv_escape_char', type=str, default=None)
    parser.add_argument('--to', dest='to', type=str, default=None, choices=["csv", "sqlite"])
    parser.add_argument('--output', dest='output', type=str, default=None)
    parser.add_argument('--limit', dest='limit', type=int, default=None,
                        help="Limit amount of source texts for prompting.")
    parser.add_argument('--limit-prompt', dest="limit_prompt", type=int, default=None,
                        help="Optional trimming prompt by the specified amount of characters.")

    native_args, model_args = CmdArgsService.partition_list(lst=sys.argv, sep="%%")

    args = parser.parse_args(args=native_args[1:])

    # Setup prompt.
    schema = SchemaService(json_data=JsonService.read_data(args.schema))

    if schema is not None:
        logger.info(f"Using schema: {schema.name}")

    model_kwargs = CmdArgsService.args_to_dict(model_args)

    # List of the Supported models and their API wrappers.
    models_preset = {
        "dynamic": lambda: dynamic_init(class_dir=CWD, class_filepath=llm_model_name,
                                        class_name=llm_model_params)(**model_kwargs)
    }

    input_providers = {
        None: lambda _: chat_with_lm(llm, chain=schema.chain, model_name=llm_model_name),
        "csv": lambda filepath: CsvService.read(target=filepath, row_id_key="uid", delimiter=args.csv_sep,
                                                as_dict=True, skip_header=True, escapechar=args.csv_escape_char),
        "jsonl": lambda filepath: JsonService.read_lines(src=filepath, row_id_key="uid")
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
            data[c] = infer_modes["default"](data[p_column])

        return data[c]

    cache_providers = {
        "sqlite": lambda filepath, table_name, data_it: SQLiteProvider.write_auto(
            data_it=data_it, target=filepath,
            data2col_func=optional_update_data_records,
            table_name=handle_table_name(table_name if table_name is not None else "contents"),
            id_column_name="uid")
    }

    output_providers = {
        "csv": lambda filepath, data_it, header:
            CsvService.write_handled(target=filepath, data_it=data_it, header=header, data2col_func=lambda v: list(v)),
        "jsonl": lambda filepath, data_it, header:
            JsonService.write_lines(target=filepath,
                                    data_it=map(lambda item: {key:item[i] for i, key in enumerate(header)}, data_it))
    }

    # Initialize LLM model.
    params = args.adapter.split(':')
    llm_model_type = params[0]
    llm_model_name = params[1] if len(params) > 1 else params[-1]
    llm_model_params = ':'.join(params[2:]) if len(params) > 2 else None
    llm = find_by_prefix(d=models_preset, key=llm_model_type)()

    # Input extension type defines the provider.
    src_filepath, src_ext, src_meta = parse_filepath(args.src)

    # Check whether we are in chat mode.
    if src_ext is None:
        input_providers[src_ext](None)
        exit(0)

    # We optionally wrap into limiter.
    queries_it = optional_limit_iter(
        it_data=map(lambda data: data.update(schema.cot_args) or data, input_providers[src_ext](src_filepath)),
        limit=args.limit)

    # Setup output.
    args.output = args.output.format(model=llm.name()) if args.output is not None else args.output
    tgt_filepath, tgt_ext, tgt_meta = parse_filepath(args.output, default_ext=args.to)

    cache_ext = "sqlite"

    cache_target = "".join(["_".join([join(CWD, basename(src_filepath)), llm.name(), schema.name]), f".{cache_ext}"]) \
        if tgt_filepath is None else tgt_filepath

    # Provide data caching.
    cache_providers[cache_ext](cache_target, table_name=tgt_meta, data_it=tqdm(queries_it, desc="Iter content"))

    # Export cached data.
    tgt_ext = src_ext if tgt_ext is None else tgt_ext
    target = "".join(["_".join([join(CWD, basename(src_filepath)), llm.name(), schema.name]), f".{tgt_ext}"]) \
        if tgt_filepath is None else tgt_filepath
    cache_table = handle_table_name(tgt_meta if tgt_meta is not None else "contents")
    output_providers[tgt_ext](
        filepath=target,
        data_it=SQLiteProvider.read(cache_target, table=cache_table),
        header=SQLiteProvider.get_columns(target=cache_target, table=cache_table))
