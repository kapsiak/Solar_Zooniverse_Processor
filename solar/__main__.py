from solar.cli import make_parser
import sys
from solar.database import create_tables

create_tables()

p = make_parser()


args = p.parse_args()
if len(sys.argv) == 1:
    p.print_help(sys.stderr)
    sys.exit(1)
args.func(args)
