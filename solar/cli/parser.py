import argparse as arg
from solar.database.tables import tables
import operator
import re
from solar.common.utils import into_number


def param_to_obj(param, table):
    param.replace(" ", "")
    comps = {"<": operator.lt, "=": operator.eq, ">": operator.gt}
    found = None
    for x in comps:
        found = param.find(x)
        if found >= 0:
            comp = x
            break

    field = param[:found]
    val = into_number(param[found + 1 :])
    field = table._meta.fields[field]
    return comps[comp](field, val)


def parse_q(args):
    table_str = args.table
    params = args.params
    (table,) = [x for x in tables if x.__name__ == table_str]
    to_pass = [param_to_obj(param, table) for param in params]
    select = table.select().where(*[to_pass])
    for x in select:
        print(x)


def make_q_parser(command_parser):
    query_parser = command_parser.add_parser(
        "query", help="Query one of the databases, if it exists"
    )

    query_parser.add_argument(
        "table", help="The table to query", choices=[x.__name__ for x in tables]
    )

    query_parser.add_argument(
        "-q", metavar="query", type=str, dest="params", action="append"
    )
    query_parser.set_defaults(func=parse_q)


def make_parser():
    root_parser = arg.ArgumentParser("Jets Processing")
    command_parser = root_parser.add_subparsers(help="Command")
    make_q_parser(command_parser)
    return root_parser
