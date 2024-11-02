import argparse
import logging
import os
import sys

from tqdm import tqdm

from os.path import join, basename

from bulk_chain.core.llm_base import BaseLM
from bulk_chain.core.provider_sqlite import SQLiteProvider
from bulk_chain.core.service_args import CmdArgsService
from bulk_chain.core.service_csv import CsvService
from bulk_chain.core.service_data import DataService
from bulk_chain.core.service_json import JsonService
from bulk_chain.core.service_llm import chat_with_lm
from bulk_chain.core.service_schema import SchemaService
from bulk_chain.core.utils import dynamic_init, find_by_prefix, handle_table_name, optional_limit_iter, parse_filepath

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


CWD = os.getcwd()


def init_llm(**model_kwargs):
    """ This method perform dynamic initialization of LLM from third-party resource.
    """

    # List of the Supported models and their API wrappers.
    models_preset = {
        "dynamic": lambda: dynamic_init(class_dir=CWD, class_filepath=llm_model_name,
                                        class_name=llm_model_params)(**model_kwargs)
    }

    # Initialize LLM model.
    params = args.adapter.split(':')
    llm_model_type = params[0]
    llm_model_name = params[1] if len(params) > 1 else params[-1]
    llm_model_params = ':'.join(params[2:]) if len(params) > 2 else None
    llm = find_by_prefix(d=models_preset, key=llm_model_type)()

    return llm, llm_model_name


def init_schema(json_filepath):
    return SchemaService(json_data=JsonService.read_data(json_filepath))


def iter_content(input_dicts_iter, llm, schema, cache_target, cache_table, id_column_name):
    """ This method represent Python API aimed at application of `llm` towards
        iterator of input_dicts via cache_target that refers to the SQLite using
        the given `schema`
    """
    assert (isinstance(llm, BaseLM))
    assert (isinstance(schema, SchemaService))
    assert (isinstance(cache_target, str))
    assert (isinstance(cache_table, str))

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
            id_column_name=id_column_name)
    }

    # We optionally wrap into limiter.
    queries_it = optional_limit_iter(
        it_data=map(lambda data: data.update(schema.cot_args) or data, input_dicts_iter),
        limit=args.limit)

    # Provide data caching.
    cache_providers["sqlite"](cache_target, table_name=tgt_meta, data_it=tqdm(queries_it, desc="Iter content"))

    return SQLiteProvider.iter_rows(cache_target, table=cache_table)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Infer Instruct LLM inference based on CoT schema")
    parser.add_argument('--adapter', dest='adapter', type=str, default=None)
    parser.add_argument('--id-col', dest='id_col', type=str, default="uid")
    parser.add_argument('--src', dest='src', type=str, default=None)
    parser.add_argument('--schema', dest='schema', type=str, default=None,
                        help="Path to the JSON file that describes schema")
    parser.add_argument('--to', dest='to', type=str, default=None, choices=["csv", "sqlite"])
    parser.add_argument('--output', dest='output', type=str, default=None)
    parser.add_argument('--limit', dest='limit', type=int, default=None,
                        help="Limit amount of source texts for prompting.")
    parser.add_argument('--limit-prompt', dest="limit_prompt", type=int, default=None,
                        help="Optional trimming prompt by the specified amount of characters.")

    native_args, model_args = CmdArgsService.partition_list(lst=sys.argv, sep="%%")

    args = parser.parse_args(args=native_args[1:])

    # Initialize Large Language Model.
    model_args_dict = CmdArgsService.args_to_dict(model_args)
    llm, llm_model_name = init_llm(**model_args_dict)

    # Setup schema.
    schema = init_schema(args.schema)
    if schema is not None:
        logger.info(f"Using schema: {schema.name}")

    input_providers = {
        None: lambda _: chat_with_lm(llm, chain=schema.chain, model_name=llm_model_name),
        "csv": lambda filepath: CsvService.read(target=filepath, row_id_key=args.id_col,
                                                as_dict=True, skip_header=True,
                                                delimiter=model_args_dict.get("delimiter", "\t"),
                                                escapechar=model_args_dict.get("escapechar", None)),
        "jsonl": lambda filepath: JsonService.read_lines(src=filepath, row_id_key=args.id_col)
    }

    output_providers = {
        "csv": lambda filepath, data_it, header:
        CsvService.write_handled(target=filepath, data_it=data_it, header=header, data2col_func=lambda v: list(v)),
        "jsonl": lambda filepath, data_it, header:
        JsonService.write_lines(target=filepath,
                                data_it=map(lambda item: {key:item[i] for i, key in enumerate(header)}, data_it))
    }

    # Setup output.
    args.output = args.output.format(model=llm.name()) if args.output is not None else args.output
    tgt_filepath, tgt_ext, tgt_meta = parse_filepath(args.output, default_ext=args.to)

    # Input extension type defines the provider.
    src_filepath, src_ext, src_meta = parse_filepath(args.src)

    # Check whether we are in chat mode.
    if src_ext is None:
        input_providers[src_ext](None)
        exit(0)

    # Setup cache target as well as the related table.
    cache_target = "".join(["_".join([join(CWD, basename(src_filepath)), llm.name(), schema.name]), f".sqlite"]) \
        if tgt_filepath is None else tgt_filepath
    cache_table = handle_table_name(tgt_meta if tgt_meta is not None else "contents")

    data_it = iter_content(input_dicts_iter=input_providers[src_ext](src_filepath),
                           schema=schema,
                           llm=llm,
                           id_column_name=args.id_col,
                           cache_target=cache_target,
                           cache_table=cache_table)

    # Setup output target
    tgt_ext = src_ext if tgt_ext is None else tgt_ext
    output_target = "".join(["_".join([join(CWD, basename(src_filepath)), llm.name(), schema.name]), f".{tgt_ext}"]) \
        if tgt_filepath is None else tgt_filepath

    # Perform output writing process.
    output_providers[tgt_ext](filepath=output_target,
                              data_it=data_it,
                              header=SQLiteProvider.get_columns(target=cache_target, table=cache_table))
