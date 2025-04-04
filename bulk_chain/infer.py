from itertools import chain
from os.path import join, basename

import argparse
import logging
import sys

from source_iter.service_csv import CsvService
from source_iter.service_jsonl import JsonlService
from tqdm import tqdm

from bulk_chain.api import INFER_MODES, _infer_batch, CWD, init_llm
from bulk_chain.core.llm_base import BaseLM
from bulk_chain.core.provider_sqlite import SQLite3Service
from bulk_chain.core.service_args import CmdArgsService
from bulk_chain.core.service_batch import BatchIterator
from bulk_chain.core.service_dict import DictionaryService
from bulk_chain.core.service_json import JsonService
from bulk_chain.core.service_schema import SchemaService
from bulk_chain.core.utils import handle_table_name, optional_limit_iter, parse_filepath

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

WRITER_PROVIDERS = {
    "sqlite": lambda filepath, table_name, data_it, **kwargs: SQLite3Service.write(
        data_it=data_it, target=filepath, table_name=table_name, skip_existed=True, **kwargs)
}

READER_PROVIDERS = {
    "sqlite": lambda filepath, table_name: SQLite3Service.read(filepath, table=table_name)
}


def infer_batch(batch, columns=None, **kwargs):
    assert (len(batch) > 0)
    # TODO. Support proper selection of columns.
    cols = batch[0].keys() if columns is None else columns
    return _infer_batch(batch=batch, cols=cols, **kwargs)


def raise_(ex):
    raise ex


def iter_content_cached(input_dicts_it, llm, schema, cache_target, batch_size, id_column_name, limit_prompt=None,
                        **cache_kwargs):
    assert (isinstance(llm, BaseLM))
    assert (isinstance(cache_target, str))

    # Quick initialization of the schema.
    if isinstance(schema, str):
        schema = JsonService.read(schema)
    if isinstance(schema, dict):
        schema = SchemaService(json_data=schema)

    # Parse target.
    cache_filepath, _, cache_table = parse_filepath(filepath=cache_target)

    # Iterator of the queries.
    prompts_it = map(
        lambda data: DictionaryService.custom_update(src_dict=data, other_dict=schema.cot_args),
        input_dicts_it
    )

    prompts_batched_it = BatchIterator(
        data_iter=iter(tqdm(prompts_it, desc="Iter Content")),
        batch_size=batch_size,
        filter_func=lambda data: not SQLite3Service.entry_exist(
            id_column_name=id_column_name, table_name=cache_table, target=cache_filepath,
            id_value=data[id_column_name], **cache_kwargs)
    )

    results_it = map(
        lambda batch: infer_batch(
            batch=batch, schema=schema,
            handle_batch_func=lambda batch: INFER_MODES["batch"](llm, batch, limit_prompt),
            handle_missed_value_func=lambda col_name: raise_(
                Exception(f"Value for {col_name} is undefined. Filling undefined values is not supported")
            )
        ),
        prompts_batched_it
    )

    # Perform caching first.
    WRITER_PROVIDERS["sqlite"](
        filepath=cache_filepath,
        table_name=cache_table,
        data_it=chain.from_iterable(results_it),
        id_column_name=id_column_name,
        **cache_kwargs)

    # Then retrieve data.
    return READER_PROVIDERS["sqlite"](filepath=cache_filepath, table_name=cache_table)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Infer Instruct LLM inference based on CoT schema")
    parser.add_argument('--adapter', dest='adapter', type=str, default=None)
    parser.add_argument('--id-col', dest='id_col', type=str, default="uid")
    parser.add_argument('--src', dest='src', type=str, nargs="?", default=None)
    parser.add_argument('--schema', dest='schema', type=str, default=None,
                        help="Path to the JSON file that describes schema")
    parser.add_argument('--to', dest='to', type=str, default=None, choices=["csv", "sqlite"])
    parser.add_argument('--output', dest='output', type=str, default=None)
    parser.add_argument('--limit', dest='limit', type=int, default=None,
                        help="Limit amount of source texts for prompting.")
    parser.add_argument('--batch-size', dest='batch_size', type=int, default=1)
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
    model_args_dict = CmdArgsService.args_to_dict(model_args) | {"attempts": 1}
    llm, llm_model_name = init_llm(adapter=args.adapter, **model_args_dict)

    # Setup schema.
    schema = SchemaService(json_data=JsonService.read(args.schema))
    schema_name = schema.src.get("name", None)
    if schema is not None:
        logger.info(f"Using schema: {schema_name}")

    input_providers = {
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

    # We do not support multiple files for other modes.
    src_filepath, src_ext, src_meta = parse_filepath(args.src)

    def default_output_file_template(ext):
        # This is a default template for output files to be generated.
        return "".join(["_".join([join(CWD, basename(src_filepath)), llm.name(), schema_name]), ext])

    # Setup cache target as well as the related table.
    cache_filepath = default_output_file_template(".sqlite") if tgt_filepath is None else tgt_filepath
    cache_table = handle_table_name(tgt_meta if tgt_meta is not None else "contents")

    # This is a content that we extracted via input provider.
    it_data = input_providers[src_ext](src_filepath)

    data_it = iter_content_cached(input_dicts_it=optional_limit_iter(it_data=it_data, limit=args.limit),
                                  limit_prompt=args.limit_prompt,
                                  schema=schema,
                                  llm=llm,
                                  batch_size=args.batch_size,
                                  id_column_name=args.id_col,
                                  cache_target=":".join([cache_filepath, cache_table]))

    # Setup output target
    tgt_ext = src_ext if tgt_ext is None else tgt_ext
    output_target = default_output_file_template(f".{tgt_ext}") if tgt_filepath is None else tgt_filepath

    # Perform output writing process.
    output_providers[tgt_ext](filepath=output_target,
                              data_it=data_it,
                              header=SQLite3Service.read_columns(target=cache_filepath, table=cache_table))
