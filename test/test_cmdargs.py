import sys
from bulk_chain.core.service_args import CmdArgsService


print(sys.argv)
string, args = CmdArgsService.partition_list(sys.argv[1:], "%%")
d = CmdArgsService.args_to_dict(args)

print(d)
