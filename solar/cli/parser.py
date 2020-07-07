import argparse as arg
from solar.cli.query import make_q_parser
from solar.cli.service import make_s_parser
from solar.cli.visual import make_v_parser
import sys


class MyParser(arg.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"error: {message}\n")
        self.print_help()
        sys.exit(2)


def make_parser():
    root_parser = MyParser("Jets Processing")
    command_parser = root_parser.add_subparsers(help="Command")
    make_q_parser(command_parser)
    make_s_parser(command_parser)
    make_v_parser(command_parser)
    return root_parser
