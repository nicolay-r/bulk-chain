class CmdArgsService:

    @staticmethod
    def autocast(v):
        for t in [int, float, str]:
            try:
                return t(v)
            except:
                pass

    @staticmethod
    def iter_arguments(lst):

        def __release():

            # We use the True value by default to treat the related parameter as flag.
            if len(buf) == 0:
                buf.append(True)

            return key, buf if len(buf) > 1 else buf[0]

        key = None
        buf = []
        for a in lst:
            if a.startswith('--'):
                # release
                if key is not None:
                    yield __release()
                # set new key and empty buf
                key = a[2:]
                buf = []
            else:
                # append argument into buffer.
                buf.append(a)

        # Sharing the remaining params.
        if key is not None:
            yield __release()

    @staticmethod
    def __find_suffix_ind(lst, idx_from, end_prefix):
        for i in range(idx_from, len(lst)):
            if lst[i].startswith(end_prefix):
                return i
        return len(lst)

    @staticmethod
    def extract_native_args(lst, end_prefix):
        return lst[:CmdArgsService.__find_suffix_ind(lst, idx_from=0, end_prefix=end_prefix)]

    @staticmethod
    def find_grouped_args(lst, starts_with, end_prefix):
        """Slices a list in two, cutting on index matching "sep"
        """

        # Checking the presence of starts_with.
        # We have to return empty content in the case of absence starts_with in the lst.
        if starts_with not in lst:
            return []

        # Assigning start index.
        idx_from = lst.index(starts_with) + 1

        # Assigning end index.
        idx_to = CmdArgsService.__find_suffix_ind(lst, idx_from=idx_from, end_prefix=end_prefix)

        return lst[idx_from:idx_to]

    @staticmethod
    def args_to_dict(args):
        return {k: CmdArgsService.autocast(v) if not isinstance(v, list) else v
                for k, v in CmdArgsService.iter_arguments(args)} if args is not None else {}
