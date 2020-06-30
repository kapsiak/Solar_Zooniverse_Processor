import argparse as arg
from solar.database.tables import tables
import operator
import re
from solar.common.utils import into_number

query_re = re.compile("([a-zA-Z1-9_]+)\s*([<=>]+)\s*([a-zA-Z1-9_-]+)")


def param_to_obj(param, table):
    comps = {
        "<": operator.lt,
        "=": operator.eq,
        ">": operator.gt,
        "<=": operator.ge,
        ">=": operator.le,
        "==": operator.eq,
    }
    matches = query_re.search(param)
    col, op, val = matches.groups()
    val = into_number(val)
    col = table._meta.fields[col]
    return comps[op](col, val)


def parse_q(args):
    table_str = args.table
    params = args.params if args.params else []
    (table,) = [x for x in tables if x.__name__ == table_str]
    to_pass = [param_to_obj(param, table) for param in params]
    select = table.select().where(*[to_pass]) if params else table.select()
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