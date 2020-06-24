from solar.cli import make_parser
import sys

p = make_parser()
args = p.parse_args()
args.func(args)
