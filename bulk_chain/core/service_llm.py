import logging

from bulk_chain.core.llm_base import BaseLM
from bulk_chain.core.service_data import DataService
from bulk_chain.core.utils import iter_params

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def pad_str(text, pad):
    return text.rjust(len(text) + pad, ' ')


def text_wrap(content, width, handle_line=lambda l: l):
    lines = []
    for text in content.split('\n'):
        for i in range(0, len(text), width):
            line = handle_line(text[i:i + width])
            lines.append(line)
    return '\n'.join(lines)


def nice_output(text, width, pad=4, remove_new_line=False):
    short_text = text.replace("\n", "") if remove_new_line else text
    return text_wrap(content=short_text, width=width, handle_line=lambda line: pad_str(line, pad=pad))


def chat_with_lm(lm, chain=None, model_name=None):
    assert(isinstance(lm, BaseLM))
    assert(isinstance(chain, list))
    assert(isinstance(model_name, str) or model_name is None)

    do_exit = False
    model_name = model_name if model_name is not None else "agent"

    while not do_exit:

        logger.info("----------------")

        # Launching the CoT engine loop.
        data_dict = {}
        for prompt_args in chain:

            # Processing the prompt.
            prompt = prompt_args["prompt"]

            # Filling necessary parameters.
            field_names = list(iter_params(prompt))
            for ind, f_name in enumerate(field_names):

                if f_name in data_dict:
                    continue

                user_input = input(f"Enter your prompt for `{f_name}` ({ind+1}/{len(field_names)}) "
                                   f"(or 'exit' to quit): ")

                if user_input.lower() == 'exit':
                    do_exit = True
                    break

                data_dict[f_name] = user_input

            if do_exit:
                break

            # Finally asking LLM.
            DataService.compose_prompt_text(prompt=prompt, data_dict=data_dict, field_names=field_names)
            actual_prompt = DataService.get_prompt_text(prompt=prompt, data_dict=data_dict)

            # Returning meta information, passed to LLM.
            pad = 4
            logger.info(pad_str(f"{model_name} (ask) ->", pad=pad))
            logger.info(nice_output(actual_prompt, pad=pad*2, remove_new_line=True, width=80))

            # Response.
            response = lm.ask(actual_prompt)
            logger.info(pad_str(f"{model_name} (resp)->", pad=pad))
            logger.info(nice_output(response, pad=pad*2, remove_new_line=False, width=80))

            # Collecting the answer for the next turn.
            data_dict[prompt_args["out"]] = response
