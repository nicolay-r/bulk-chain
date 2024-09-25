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
        if len(buf) > 0:
            yield __release()

    @staticmethod
    def partition_list(lst, sep):
        """Slices a list in two, cutting on index matching "sep"
        """
        if sep in lst:
            idx = lst.index(sep)
            return (lst[:idx], lst[idx+1:])
        else:
            return (lst[:], None)

    @staticmethod
    def args_to_dict(args):
        return {k: CmdArgsService.autocast(v) if not isinstance(v, list) else v
                for k, v in CmdArgsService.iter_arguments(args)} if args is not None else {}
