from bulk_chain.core.llm_base import BaseLM
from bulk_chain.core.service_data import DataService
from bulk_chain.core.utils import iter_params
from bulk_chain.core.utils_logger import StreamedLogger


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


def chat_with_lm(lm, preset_dict=None, chain=None, model_name=None, line_width=80, pad=0):
    assert (isinstance(lm, BaseLM))
    assert (isinstance(chain, list))
    assert (isinstance(model_name, str) or model_name is None)

    preset_dict = {} if preset_dict is None else preset_dict

    streamed_logger = StreamedLogger(__name__)

    do_exit = False
    model_name = model_name if model_name is not None else "agent"

    while not do_exit:

        streamed_logger.info("----------------")
        streamed_logger.info("\n")

        # Launching the CoT engine loop.
        data_dict = {} | preset_dict
        for chain_ind, prompt_args in enumerate(chain):

            # Processing the prompt.
            prompt = prompt_args["prompt"]

            # Filling necessary parameters.
            user_informed = False
            field_names = list(iter_params(prompt))
            for ind, f_name in enumerate(field_names):

                if f_name in data_dict:
                    continue

                user_input = input(f"Enter your prompt for `{f_name}` ({ind+1}/{len(field_names)}) "
                                   f"(or 'exit' to quit): ")
                user_informed = True

                if user_input.lower() == 'exit':
                    do_exit = True
                    break

                data_dict[f_name] = user_input

            if do_exit:
                break

            # In the case of the initial interaction with the chain.
            # we make sure that aware user for starting interaction.
            if chain_ind == 0 and not user_informed:
                user_input = input(f"Enter to continue (or 'exit' to quit) ...")
                if user_input.lower() == 'exit':
                    do_exit = True

            # Finally asking LLM.
            DataService.compose_prompt_text(prompt=prompt, data_dict=data_dict, field_names=field_names)
            actual_prompt = DataService.get_prompt_text(prompt=prompt, data_dict=data_dict)

            # Returning meta information, passed to LLM.
            streamed_logger.info(pad_str(f"{model_name} (ask [{chain_ind+1}/{len(chain)}]) ->", pad=pad))
            streamed_logger.info("\n")
            streamed_logger.info(nice_output(actual_prompt, pad=pad, remove_new_line=True, width=line_width))
            streamed_logger.info("\n\n")

            # Response.
            response = lm.ask_core(batch=[actual_prompt])[0]
            streamed_logger.info(pad_str(f"{model_name} (resp [{chain_ind+1}/{len(chain)}])->", pad=pad))
            streamed_logger.info("\n")
            if isinstance(response, str):
                streamed_logger.info(nice_output(response, pad=pad, remove_new_line=False, width=line_width))
                buffer = [response]
            else:
                buffer = []
                for chunk in response:
                    streamed_logger.info(chunk)
                    buffer.append(str(chunk))

            streamed_logger.info("\n\n")

            # Collecting the answer for the next turn.
            data_dict[prompt_args["out"]] = "".join(buffer)
