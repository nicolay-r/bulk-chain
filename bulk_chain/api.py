import collections
import os
from itertools import chain

from bulk_chain.core.llm_base import BaseLM
from bulk_chain.core.service_batch import BatchIterator
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


def _iter_entry_content(entry, entry_info=None, **kwargs):

    if isinstance(entry, str):
        kwargs.get("callback_str_func", lambda *_: None)(entry, entry_info)
        yield entry
    elif isinstance(entry, collections.abc.Iterable):
        h = kwargs.get("callback_stream_func", lambda *_: None)
        h(None, entry_info | {"action": "start"})
        for chunk in map(lambda item: str(item), entry):
            yield chunk
            h(chunk, entry_info)
        h(None, entry_info | {"action": "end"})
    else:
        raise Exception(f"Non supported type `{type(entry)}` for handling output from batch")


def _iter_batch_prompts(c, batch_content_it, **kwargs):
    for ind_in_batch, entry in enumerate(batch_content_it):
        content = DataService.get_prompt_text(
            prompt=entry[c]["prompt"],
            data_dict=entry,
            handle_missed_func=kwargs["handle_missed_value_func"])
        yield ind_in_batch, content


def _iter_batch_responses(p_column, c, batch_content_it, **kwargs):
    p_batch = [item[p_column] for item in batch_content_it]
    # TODO. This part could be async.
    # TODO. ind_in_batch might be a part of the async return.
    for ind_in_batch, entry in enumerate(kwargs["handle_batch_func"](p_batch)):
        yield ind_in_batch, _iter_entry_content(entry=entry, entry_info={"ind": ind_in_batch, "param": c}, **kwargs)


def _infer_batch(batch, schema, return_mode, cols=None, **kwargs):
    assert (isinstance(batch, list))

    if len(batch) == 0:
        return batch

    if cols is None:
        first_item = batch[0]
        cols = list(first_item.keys()) if cols is None else cols

    for c in cols:

        # Handling prompt column.
        if c in schema.p2r:
            content_it = _iter_batch_prompts(c=c, batch_content_it=iter(batch), **kwargs)
            for ind_in_batch, prompt in content_it:
                batch[ind_in_batch][c] = prompt

        # Handling column for inference.
        if c in schema.r2p:
            content_it = _iter_batch_responses(c=c, p_column=schema.r2p[c], batch_content_it=iter(batch), **kwargs)
            for ind_in_batch, chunk_it in content_it:

                chunks = []
                for chunk in chunk_it:
                    chunks.append(chunk)

                    if return_mode == "chunk":
                        yield [ind_in_batch, c, chunk]

                batch[ind_in_batch][c] = "".join(chunks)

    if return_mode == "record":
        for record in batch:
            yield record

    if return_mode == "batch":
        yield batch


def iter_content(input_dicts_it, llm, schema, batch_size=1, limit_prompt=None, return_mode="batch", **kwargs):
    """ This method represent Python API aimed at application of `llm` towards
        iterator of input_dicts via cache_target that refers to the SQLite using
        the given `schema`
    """
    assert (return_mode in ["batch", "chunk"])
    assert (isinstance(llm, BaseLM))

    # Quick initialization of the schema.
    if isinstance(schema, str):
        schema = JsonService.read(schema)
    if isinstance(schema, dict):
        schema = SchemaService(json_data=schema)

    prompts_it = map(
        lambda data: DictionaryService.custom_update(src_dict=dict(data), other_dict=schema.cot_args),
        input_dicts_it
    )

    content_it = (_infer_batch(batch=batch,
                               handle_batch_func=lambda batch: INFER_MODES["batch"](llm, batch, limit_prompt),
                               return_mode=return_mode,
                               schema=schema,
                               **kwargs)
                  for batch in BatchIterator(prompts_it, batch_size=batch_size))

    yield from chain.from_iterable(content_it)


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
