class BatchService(object):

    @staticmethod
    def handle_param(batch, param, handle_func):
        for item in batch:
            item[param] = handle_func(item[param])

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