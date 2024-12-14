import os
from os.path import join, basename

import argparse
import logging
import sys

from tqdm import tqdm

from source_iter.service_csv import CsvService
from source_iter.service_jsonl import JsonlService
from source_iter.service_sqlite import SQLite3Service

from bulk_chain.core.llm_base import BaseLM
from bulk_chain.core.service_args import CmdArgsService
from bulk_chain.core.service_data import DataService
from bulk_chain.core.service_json import JsonService
from bulk_chain.core.service_llm import chat_with_lm
from bulk_chain.core.service_schema import SchemaService
from bulk_chain.core.utils import dynamic_init, find_by_prefix, handle_table_name, optional_limit_iter, parse_filepath

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


CWD = os.getcwd()


INFER_MODES = {
    "default": lambda llm, prompt, limit_prompt=None: llm.ask_safe(
        prompt[:limit_prompt] if limit_prompt is not None else prompt)
}


WRITER_PROVIDERS = {
    "sqlite": lambda filepath, table_name, data_it, infer_data_func, **kwargs: SQLite3Service.write(
        data_it=data_it, target=filepath, table_name=table_name, data2col_func=infer_data_func,
        skip_existed=True, **kwargs)
}


READER_PROVIDERS = {
    "sqlite": lambda filepath, table_name: SQLite3Service.read(filepath, table=table_name)
}


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
    return SchemaService(json_data=JsonService.read(json_filepath))


def optional_update_data_records(c, data, schema, infer_func):
    assert (isinstance(c, str))

    if c in schema.p2r:
        data[c] = DataService.get_prompt_text(prompt=data[c]["prompt"], data_dict=data)
    if c in schema.r2p:
        p_column = schema.r2p[c]
        # This instruction takes a lot of time in a non-batching mode.
        data[c] = infer_func(data[p_column])

    return data[c]


def iter_content(input_dicts_it, llm, schema, cache_target=None, limit_prompt=None, **cache_kwargs):
    """ This method represent Python API aimed at application of `llm` towards
        iterator of input_dicts via cache_target that refers to the SQLite using
        the given `schema`
    """
    assert (isinstance(llm, BaseLM))
    assert (isinstance(schema, SchemaService))
    assert (isinstance(cache_target, str) or cache_target is None)

    def __infer_query(data_record, cols=None):
        cols = data_record.keys() if cols is None else cols
        for c in cols:
            optional_update_data_records(c=c, data=data_record, schema=schema,
                                         infer_func=lambda prompt: INFER_MODES["default"](llm, prompt, limit_prompt))
        return data_record

    # Provide schema COT args.
    queries_it = map(lambda data: data.update(schema.cot_args) or data, input_dicts_it)

    if cache_target is None:
        return (__infer_query(q) for q in queries_it)

    # Parse target.
    cache_filepath, _, cache_table = parse_filepath(filepath=cache_target)
    # Perform caching first.
    WRITER_PROVIDERS["sqlite"](filepath=cache_filepath, table_name=cache_table,
                               data_it=tqdm(queries_it, desc="Iter content"),
                               infer_data_func=lambda c, query: __infer_query(query, cols=[c])[c],
                               **cache_kwargs)
    # Then retrieve data.
    return READER_PROVIDERS["sqlite"](filepath=cache_filepath, table_name=cache_table)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Infer Instruct LLM inference based on CoT schema")
    parser.add_argument('--adapter', dest='adapter', type=str, default=None)
    parser.add_argument('--attempts', dest='attempts', type=int, default=None)
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

    # Extract native arguments.
    native_args = CmdArgsService.extract_native_args(sys.argv, end_prefix="%%")
    args = parser.parse_args(args=native_args[1:])

    # Extract csv-related arguments.
    csv_args = CmdArgsService.find_grouped_args(lst=sys.argv, starts_with="%%csv", end_prefix="%%")
    csv_args_dict = CmdArgsService.args_to_dict(csv_args)

    # Extract model-related arguments and Initialize Large Language Model.
    model_args = CmdArgsService.find_grouped_args(lst=sys.argv, starts_with="%%m", end_prefix="%%")
    model_args_dict = CmdArgsService.args_to_dict(model_args) | {"attempts": args.attempts}
    llm, llm_model_name = init_llm(**model_args_dict)

    # Setup schema.
    schema = init_schema(args.schema)
    if schema is not None:
        logger.info(f"Using schema: {schema.name}")

    input_providers = {
        None: lambda _: chat_with_lm(llm, chain=schema.chain, model_name=llm_model_name),
        "csv": lambda filepath: CsvService.read(src=filepath, row_id_key=args.id_col,
                                                as_dict=True, skip_header=True,
                                                delimiter=csv_args_dict.get("delimiter", ","),
                                                escapechar=csv_args_dict.get("escapechar", None)),
        "tsv": lambda filepath: CsvService.read(src=filepath, row_id_key=args.id_col,
                                                as_dict=True, skip_header=True,
                                                delimiter=csv_args_dict.get("delimiter", "\t"),
                                                escapechar=csv_args_dict.get("escapechar", None)),
        "jsonl": lambda filepath: JsonlService.read(src=filepath, row_id_key=args.id_col)
    }

    output_providers = {
        "csv": lambda filepath, data_it, header: CsvService.write(target=filepath,
                                                                  data_it=data_it, header=header,
                                                                  delimiter=csv_args_dict.get("delimiter", ","),
                                                                  escapechar=csv_args_dict.get("escapechar", None),
                                                                  it_type=None),
        "tsv": lambda filepath, data_it, header: CsvService.write(target=filepath,
                                                                  data_it=data_it, header=header,
                                                                  delimiter=csv_args_dict.get("delimiter", "\t"),
                                                                  escapechar=csv_args_dict.get("escapechar", None),
                                                                  it_type=None),
        "jsonl": lambda filepath, data_it, header:
        JsonlService.write(target=filepath,
                           data_it=map(lambda item: {key: item[i] for i, key in enumerate(header)}, data_it))
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

    def default_output_file_template(ext):
        # This is a default template for output files to be generated.
        return "".join(["_".join([join(CWD, basename(src_filepath)), llm.name(), schema.name]), ext])

    # Setup cache target as well as the related table.
    cache_filepath = default_output_file_template(".sqlite") if tgt_filepath is None else tgt_filepath
    cache_table = handle_table_name(tgt_meta if tgt_meta is not None else "contents")

    # This is a content that we extracted via input provider.
    it_data = input_providers[src_ext](src_filepath)

    data_it = iter_content(input_dicts_it=optional_limit_iter(it_data=it_data, limit=args.limit),
                           limit_prompt=args.limit_prompt,
                           schema=schema,
                           llm=llm,
                           id_column_name=args.id_col,
                           cache_target=":".join([cache_filepath, cache_table]))

    # Setup output target
    tgt_ext = src_ext if tgt_ext is None else tgt_ext
    output_target = default_output_file_template(f".{tgt_ext}") if tgt_filepath is None else tgt_filepath

    # Perform output writing process.
    output_providers[tgt_ext](filepath=output_target,
                              data_it=data_it,
                              header=SQLite3Service.read_columns(target=cache_filepath, table=cache_table))
