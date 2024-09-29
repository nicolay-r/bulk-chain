import unittest

from bulk_chain.core.utils import iter_params


class TestArgumentsSeeking(unittest.TestCase):

    def test(self):
        params = list(iter_params("X is a {x} and p is {text} and for {k}"))

        line = ",".join(["{{{x}}}".format(x=x) for x in params])
        print(line)
        d_params = {}
        for param in params:
            d_params[param] = 2
        print(d_params)

        z = line.format(**d_params)
        print(z)

        b = list(iter_params("X"))
        print(b)


if __name__ == '__main__':
    unittest.main()
