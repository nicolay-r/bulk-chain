import collections
import logging
import os
from itertools import chain
from typing import AsyncGenerator

from bulk_chain.core.llm_base import BaseLM
from bulk_chain.core.service_asyncio import AsyncioService
from bulk_chain.core.service_batch import BatchIterator
from bulk_chain.core.service_data import DataService
from bulk_chain.core.service_dict import DictionaryService
from bulk_chain.core.service_json import JsonService
from bulk_chain.core.service_schema import SchemaService
from bulk_chain.core.utils import attempt_wrapper

INFER_MODES = {
    "single": lambda llm, batch: [llm.ask(prompt) for prompt in batch],
    "single_stream": lambda llm, batch: [llm.ask_stream(prompt) for prompt in batch],
    "batch": lambda llm, batch: llm.ask(batch),
    "batch_async": lambda llm, batch: AsyncioService.run_tasks(batch=batch, async_handler=llm.ask_async),
    "batch_stream_async": lambda llm, batch: NotImplemented()
}


CWD = os.getcwd()


def _iter_entry_content(entry):

    if isinstance(entry, str):
        yield entry
    elif isinstance(entry, collections.abc.Iterable):
        for chunk in map(lambda item: str(item), entry):
            yield chunk
    elif isinstance(entry, AsyncGenerator):
        raise Exception("Not Supported Yet!")
    else:
        raise Exception(f"Non supported type `{type(entry)}` for handling output from batch")


def _iter_batch_prompts(c, batch_content_it, **kwargs):
    for ind_in_batch, entry in enumerate(batch_content_it):
        content = DataService.get_prompt_text(
            prompt=entry[c]["prompt"],
            data_dict=entry,
            handle_missed_func=kwargs["handle_missed_value_func"])
        yield ind_in_batch, content


def _iter_batch_responses(p_column, batch_content_it, **kwargs):
    p_batch = [item[p_column] for item in batch_content_it]
    for ind_in_batch, entry in enumerate(kwargs["handle_batch_func"](p_batch)):
        yield ind_in_batch, _iter_entry_content(entry=entry)


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
            content_it = _iter_batch_responses(p_column=schema.r2p[c], batch_content_it=iter(batch), **kwargs)
            for ind_in_batch, chunk_it in content_it:
                for chunk in chunk_it:
                    # Register new list if needed.
                    if batch[ind_in_batch][c] is None:
                        batch[ind_in_batch][c] = []
                    # Append batch.
                    batch[ind_in_batch][c].append(chunk)
                    # Returning (optional).
                    if return_mode == "chunk":
                        yield [ind_in_batch, c, chunk]

            # Convert content to string.
            for item in batch:
                item[c] = "".join(item[c])

    if return_mode == "record":
        for record in batch:
            yield record

    if return_mode == "batch":
        yield batch


def iter_content(input_dicts_it, llm, schema, batch_size=1, limit_prompt=None,
                 infer_mode="batch", return_mode="batch", attempts=1, **kwargs):
    """ This method represent Python API aimed at application of `llm` towards
        iterator of input_dicts via cache_target that refers to the SQLite using
        the given `schema`
    """
    assert (infer_mode in INFER_MODES.keys())
    assert (return_mode in ["batch", "chunk", "record"])
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

    handle_batch_func = lambda batch: INFER_MODES[infer_mode](
        llm, DataService.limit_prompts(batch, limit=limit_prompt)
    )

    # Optional wrapping into attempts.
    if attempts > 1:
        # Optional setup of the logger.
        logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        attempt_dec = attempt_wrapper(attempts=attempts,
                                      delay_sec=kwargs.get("attempt_delay_sec", 1),
                                      logger=logger)
        handle_batch_func = attempt_dec(handle_batch_func)

    content_it = (_infer_batch(batch=batch,
                               handle_batch_func=handle_batch_func,
                               handle_missed_value_func=lambda *_: None,
                               return_mode=return_mode,
                               schema=schema,
                               **kwargs)
                  for batch in BatchIterator(prompts_it, batch_size=batch_size))

    yield from chain.from_iterable(content_it)
