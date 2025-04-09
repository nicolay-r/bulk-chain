import importlib
import logging
import sys
from collections import Counter
from os.path import dirname, join, basename

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def find_by_prefix(d, key):
    """
        d: dict (str, val).
    """
    assert(isinstance(d, dict))
    assert(isinstance(key, str))

    # We first check the full match.
    for k, value in d.items():
        if k == key:
            return value

    # If we can't establish full match, then we seek by prefix.
    matches = []
    for k, value in d.items():
        if key.startswith(k):
            matches.append(k)

    if len(matches) > 1:
        raise Exception(f"There are multiple entries that are related to `{key}`: {matches}")
    if len(matches) == 0:
        raise Exception(f"No entries were found for {key}!")

    return d[matches[0]]


def iter_params(text):
    assert(isinstance(text, str))
    beg = 0
    while beg < len(text):
        try:
            pb = text.index('{', beg)
        except ValueError:
            break
        pe = text.index('}', beg+1)
        # Yield argument.
        yield text[pb+1:pe]
        beg = pe+1


def auto_import(name, is_class=False):
    """ Import from the external python packages.
    """
    def __get_module(comps_list):
        return importlib.import_module(".".join(comps_list))

    components = name.split('.')
    m = getattr(__get_module(components[:-1]), components[-1])

    return m() if is_class else m


def dynamic_init(class_dir, class_filepath, class_name=None):

    # Registering path.
    target = join(class_dir, dirname(class_filepath))
    logger.info(f"Adding sys path for `{target}`")
    sys.path.insert(1, target)
    class_path_list = class_filepath.split('/')

    # Composing proper class name.
    class_filename = basename(class_path_list[-1])
    if class_filename.endswith(".py"):
        class_filename = class_filename[:-len(".py")]

    # Loading library.
    class_name = class_path_list[-1].title() if class_name is None else class_name
    class_path = ".".join([class_filename, class_name])
    logger.info(f"Dynamic loading for the file and class `{class_path}`")
    cls = auto_import(class_path, is_class=False)

    return cls


def optional_limit_iter(it_data, limit=None):
    counter = Counter()
    for data in it_data:
        counter["returned"] += 1
        if limit is not None and counter["returned"] > limit:
            break
        yield data
