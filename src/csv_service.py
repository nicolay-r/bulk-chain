import csv


class CsvService:

    @staticmethod
    def write(target, lines_it):
        f = open(target, "w")
        print(f"Saving: {target}")
        w = csv.writer(f, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for content in lines_it:
            w.writerow(content)

    @staticmethod
    def write_handled(target, data_it, data2col_func, header):

        def __it():
            yield ["row_id"] + header
            for row_id, data in data_it:
                content = data2col_func(data)
                assert(len(content) == len(header))
                yield [row_id] + content

        CsvService.write(target, lines_it=__it())

    @staticmethod
    def read(target, delimiter='\t', quotechar='"', skip_header=False, cols=None, return_row_ids=False):
        assert(isinstance(cols, list) or cols is None)

        header = None
        with open(target, newline='\n') as f:
            for row_id, row in enumerate(csv.reader(f, delimiter=delimiter, quotechar=quotechar)):
                if skip_header and row_id == 0:
                    header = row
                    continue

                # Determine the content we wish to return.
                if cols is None:
                    content = row
                else:
                    row_d = {header[col_name]: value for col_name, value in enumerate(row)}
                    content = [row_d[col_name] for col_name in cols]

                # Optionally attach row_id to the content.
                yield [row_id] + content if return_row_ids else content