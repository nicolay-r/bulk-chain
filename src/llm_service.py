from src.lm.base import BaseLM


def chat_with_lm(lm, do_exit):
    assert(isinstance(lm, BaseLM))

    while True:
        user_input = input("Enter your prompt (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        response = lm.ask(user_input)
        print(response)

    if do_exit:
        exit(0)