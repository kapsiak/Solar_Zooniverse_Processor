from solar.cli import make_parser
import sys

p = make_parser()
args = p.parse_args()
if len(sys.argv) == 1:
    p.print_help(sys.stderr)
    sys.exit(1)
args.func(args)
