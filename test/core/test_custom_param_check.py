import unittest

from bulk_chain.api import iter_content
from bulk_chain.core.llm_base import BaseLM
from bulk_chain.core.utils import check_is_param_name, iter_params


class EchoLM(BaseLM):
    """ Local mock that echoes back the resolved prompt (no network).
    """

    def ask(self, prompt, **kwargs):
        return "ECHO:" + prompt


# `item2` contains a digit, so the default `check_is_param_name` rejects it,
# while it is still a valid `str.format` placeholder.
ALNUM_CHECK = lambda name: name.replace("_", "").isalnum()


class TestCustomParamCheck(unittest.TestCase):

    def test_iter_params_default(self):
        params = list(iter_params("a {x} b {item2} c {my_param}"))
        self.assertEqual(params, ["x", "my_param"])

    def test_iter_params_custom_checker(self):
        params = list(iter_params("a {x} b {item2} c {my_param}",
                                  check_param_name_func=ALNUM_CHECK))
        self.assertEqual(params, ["x", "item2", "my_param"])

    def test_iter_params_default_is_explicit_default(self):
        text = "a {x} b {item2} c {my_param}"
        self.assertEqual(
            list(iter_params(text)),
            list(iter_params(text, check_param_name_func=check_is_param_name)))

    def test_iter_params_rejects_non_callable(self):
        with self.assertRaises(AssertionError):
            list(iter_params("{x}", check_param_name_func="not-callable"))

    def _run_single(self, **kwargs):
        schema = {"schema": [{"prompt": "val={item2}", "out": "response"}]}
        data = [{"item2": "HELLO"}]
        results = list(iter_content(input_dicts_it=[dict(d) for d in data],
                                    llm=EchoLM(),
                                    schema=schema,
                                    **kwargs))
        self.assertEqual(len(results), 1)
        return results[0]

    def test_iter_content_default_leaves_placeholder(self):
        record = self._run_single()
        self.assertEqual(record["response"], "ECHO:val={item2}")

    def test_iter_content_custom_checker_kwarg(self):
        record = self._run_single(check_param_name_func=ALNUM_CHECK)
        self.assertEqual(record["response"], "ECHO:val=HELLO")


if __name__ == '__main__':
    unittest.main()
