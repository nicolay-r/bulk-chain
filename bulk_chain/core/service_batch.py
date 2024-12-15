class BatchService(object):

    @staticmethod
    def handle_param_as_batch(batch, src_param, tgt_param, handle_func):
        assert (isinstance(batch, list))
        assert (isinstance(src_param, str))
        assert (callable(handle_func))

        _batch = [item[src_param] for item in batch]

        # Do handling for the batch.
        _handled_batch = handle_func(_batch)
        assert (isinstance(_handled_batch, list))

        # Apply changes.
        for i, item in enumerate(batch):
            item[tgt_param] = _handled_batch[i]


class BatchIterator:

    def __init__(self, data_iter, batch_size, end_value=None):
        assert(isinstance(batch_size, int) and batch_size > 0)
        assert(callable(end_value) or end_value is None)
        self.__data_iter = data_iter
        self.__index = 0
        self.__batch_size = batch_size
        self.__end_value = end_value

    def __iter__(self):
        return self

    def __next__(self):
        buffer = []
        while True:
            try:
                data = next(self.__data_iter)
            except StopIteration:
                break
            buffer.append(data)
            if len(buffer) == self.__batch_size:
                break

        if len(buffer) > 0:
            self.__index += 1
            return buffer

        if self.__end_value is None:
            raise StopIteration
        else:
            return self.__end_value()
