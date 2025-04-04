import collections
import os
from itertools import chain

from bulk_chain.core.llm_base import BaseLM
from bulk_chain.core.service_batch import BatchIterator, BatchService
from bulk_chain.core.service_data import DataService
from bulk_chain.core.service_dict import DictionaryService
from bulk_chain.core.service_json import JsonService
from bulk_chain.core.service_schema import SchemaService
from bulk_chain.core.utils import dynamic_init, find_by_prefix


INFER_MODES = {
    "batch": lambda llm, batch, limit_prompt=None: llm.ask_core(
        DataService.limit_prompts(batch, limit=limit_prompt))
}


CWD = os.getcwd()


def _handle_entry(entry, entry_info=None, **kwargs):

    if isinstance(entry, str):
        kwargs.get("callback_str_func", lambda *_: None)(entry, entry_info)
        return entry
    elif isinstance(entry, collections.abc.Iterable):
        chunks = []
        h = kwargs.get("callback_stream_func", lambda *_: None)

        h(None, entry_info | {"action": "start"})

        for chunk in map(lambda item: str(item), entry):
            chunks.append(chunk)
            h(chunk, entry_info)

        h(None, entry_info | {"action": "end"})

        return "".join(chunks)

    raise Exception(f"Non supported type `{type(entry)}` for handling output from batch")


def _update_batch_content(c, batch, schema, **kwargs):
    assert (isinstance(batch, list))
    assert (isinstance(c, str))

    if c in schema.p2r:
        for batch_item in batch:
            batch_item[c] = DataService.get_prompt_text(
                prompt=batch_item[c]["prompt"],
                data_dict=batch_item,
                handle_missed_func=kwargs["handle_missed_value_func"])
    if c in schema.r2p:
        p_column = schema.r2p[c]
        # This instruction takes a lot of time in a non-batching mode.
        BatchService.handle_param_as_batch(
            batch=batch,
            src_param=p_column,
            tgt_param=c,
            handle_batch_func=lambda b: kwargs["handle_batch_func"](b),
            handle_entry_func=lambda entry, info: _handle_entry(entry=entry, entry_info=info, **kwargs)
        )


def _infer_batch(batch, schema, cols=None, **kwargs):
    assert (isinstance(batch, list))

    if len(batch) == 0:
        return batch

    if cols is None:
        first_item = batch[0]
        cols = list(first_item.keys()) if cols is None else cols

    for c in cols:
        _update_batch_content(c=c, batch=batch, schema=schema, **kwargs)

    return batch


def iter_content(input_dicts_it, llm, schema, batch_size=1, return_batch=True, limit_prompt=None, **kwargs):
    """ This method represent Python API aimed at application of `llm` towards
        iterator of input_dicts via cache_target that refers to the SQLite using
        the given `schema`
    """
    assert (isinstance(llm, BaseLM))

    # Quick initialization of the schema.
    if isinstance(schema, str):
        schema = JsonService.read(schema)
    if isinstance(schema, dict):
        schema = SchemaService(json_data=schema)

    prompts_it = map(
        lambda data: DictionaryService.custom_update(src_dict=data, other_dict=schema.cot_args),
        input_dicts_it
    )

    content_it = (_infer_batch(batch=batch,
                               handle_batch_func=lambda batch: INFER_MODES["batch"](llm, batch, limit_prompt),
                               schema=schema,
                               **kwargs)
                  for batch in BatchIterator(prompts_it, batch_size=batch_size))

    yield from content_it if return_batch else chain.from_iterable(content_it)


def init_llm(adapter, **model_kwargs):
    """ This method perform dynamic initialization of LLM from third-party resource.
    """
    assert (isinstance(adapter, str))

    # List of the Supported models and their API wrappers.
    models_preset = {
        "dynamic": lambda: dynamic_init(class_dir=CWD, class_filepath=llm_model_name,
                                        class_name=llm_model_params)(**model_kwargs)
    }

    # Initialize LLM model.
    params = adapter.split(':')
    llm_model_type = params[0]
    llm_model_name = params[1] if len(params) > 1 else params[-1]
    llm_model_params = ':'.join(params[2:]) if len(params) > 2 else None
    llm = find_by_prefix(d=models_preset, key=llm_model_type)()

    return llm, llm_model_name
