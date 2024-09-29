import csv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CsvService:

    @staticmethod
    def write(target, lines_it):
        f = open(target, "w")
        logger.info(f"Saving: {target}")
        w = csv.writer(f, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for content in lines_it:
            w.writerow(content)

    @staticmethod
    def write_handled(target, data_it, data2col_func, header):

        def __it():
            yield header
            for data in data_it:
                content = data2col_func(data)
                assert(len(content) == len(header))
                yield content

        CsvService.write(target, lines_it=__it())

    @staticmethod
    def read(target, skip_header=False, cols=None, as_dict=False, row_id_key=None, **csv_kwargs):
        assert (isinstance(row_id_key, str) or row_id_key is None)
        assert (isinstance(cols, list) or cols is None)

        header = None
        with open(target, newline='\n') as f:
            for row_id, row in enumerate(csv.reader(f, **csv_kwargs)):
                if skip_header and row_id == 0:
                    header = ([row_id_key] if row_id_key is not None else []) + row
                    continue

                # Determine the content we wish to return.
                if cols is None:
                    content = row
                else:
                    row_d = {header[col_ind]: value for col_ind, value in enumerate(row)}
                    content = [row_d[col_name] for col_name in cols]

                content = ([row_id-1] if row_id_key is not None else []) + content

                # Optionally attach row_id to the content.
                if as_dict:
                    assert (header is not None)
                    assert (len(content) == len(header))
                    yield {k: v for k, v in zip(header, content)}
                else:
                    yield content
