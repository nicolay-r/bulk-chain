import importlib
import logging
import sys
from collections import Counter

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


def format_model_name(name):
    return name.replace("/", "_")


def parse_filepath(filepath, default_filepath=None, default_ext=None):
    """ This is an auxiliary function for handling sources and targets from cmd string.
    """
    if filepath is None:
        return default_filepath, default_ext, None
    info = filepath.split(":")
    filepath = info[0]
    meta = info[1] if len(info) > 1 else None
    ext = filepath.split('.')[-1] if default_ext is None else default_ext
    return filepath, ext, meta


def handle_table_name(name):
    return name.\
        replace('-', '_').\
        replace('.', "_")


def auto_import(name, is_class=False):
    """ Import from the external python packages.
    """
    def __get_module(comps_list):
        return importlib.import_module(".".join(comps_list))

    components = name.split('.')
    m = getattr(__get_module(components[:-1]), components[-1])

    return m() if is_class else m


def dynamic_init(class_dir, class_filepath, class_name=None):
    sys.path.append(class_dir)
    class_path_list = class_filepath.split('/')
    class_path_list[-1] = '.'.join(class_path_list[-1].split('.')[:-1])
    class_name = class_path_list[-1].title() if class_name is None else class_name
    class_path = ".".join(class_path_list + [class_name])
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
