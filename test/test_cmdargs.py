import sys

from bulk_chain.core.service_args import CmdArgsService


# Csv-related.
csv_args = CmdArgsService.find_grouped_args(sys.argv, starts_with="%%csv", end_prefix="%%")
print(csv_args)
csv_args = CmdArgsService.args_to_dict(csv_args)
print("csv\t", csv_args)

# Model-related.
m_args = CmdArgsService.find_grouped_args(sys.argv, starts_with="%%m", end_prefix="%%")
m_args = CmdArgsService.args_to_dict(m_args)
print("mod\t", m_args)

# native.
n_args = CmdArgsService.extract_native_args(sys.argv, end_prefix="%%")
n_args = CmdArgsService.args_to_dict(n_args)
print("nat\t", n_args)
