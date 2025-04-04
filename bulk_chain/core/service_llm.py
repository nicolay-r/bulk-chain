from bulk_chain.api import iter_content
from bulk_chain.core.llm_base import BaseLM
from bulk_chain.core.utils_logger import StreamedLogger


def pad_str(text, pad):
    return text.rjust(len(text) + pad, ' ')


def nice_output(text, remove_new_line=False):
    short_text = text.replace("\n", "") if remove_new_line else text
    return short_text


def chat_with_lm(lm, preset_dict=None, schema=None, model_name=None, pad=0):
    assert (isinstance(lm, BaseLM))
    assert (isinstance(model_name, str) or model_name is None)

    preset_dict = {} if preset_dict is None else preset_dict

    streamed_logger = StreamedLogger(__name__)
    do_exit = False
    model_name = model_name if model_name is not None else "agent"

    while not do_exit:

        # Launching the CoT engine loop.
        data_dict = {} | preset_dict

        def callback_str_func(entry, info):
            streamed_logger.info(pad_str(f"{model_name} ({info['param']})->\n", pad=pad))
            streamed_logger.info(nice_output(entry, remove_new_line=False))
            streamed_logger.info("\n\n")

        def handle_missed_value(col_name):
            user_input = input(f"Enter your prompt for `{col_name}`"
                               f"(or 'exit' to quit): ")

            if user_input.lower() == 'exit':
                exit(0)

            return user_input

        def callback_stream_func(entry, info):
            if entry is None and info["action"] == "start":
                streamed_logger.info(pad_str(f"{model_name} ({info['param']})->\n", pad=pad))
                return
            if entry is None and info["action"] == "end":
                streamed_logger.info("\n\n")
                return

            streamed_logger.info(entry)

        content_it = iter_content(
            input_dicts_it=[data_dict],
            llm=lm,
            schema=schema,
            batch_size=1,
            return_batch=True,
            handle_missed_value_func=handle_missed_value,
            callback_str_func=callback_str_func,
            callback_stream_func=callback_stream_func,
        )

        for _ in content_it:
            user_input = input(f"Enter to continue (or 'exit' to quit) ...\n")
            if user_input.lower() == 'exit':
                do_exit = True