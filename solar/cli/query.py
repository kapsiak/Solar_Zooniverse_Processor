import argparse as arg
from solar.database.tables import tables
import operator
import re
from solar.common.utils import into_number
from functools import reduce

query_re = re.compile("([a-zA-Z0-9_]+)\s*([<=>]+)\s*([a-zA-Z0-9_-]+)")


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
    print(val)
    if "time" in col:
        pass
    col = table._meta.fields[col]
    return comps[op](col, val)


def parse_q(args):
    table_str = args.table
    update = args.update
    params = args.params if args.params else []
    (table,) = [x for x in tables if x.__name__ == table_str]
    to_pass = [param_to_obj(param, table) for param in params]
    select = (
        table.select().where(reduce(operator.and_, to_pass))
        if params
        else table.select()
    )
    for x in select:
        print(x)
    if update:
        try:
            print("Updating table")
            table.update_table()
        except Exception as e:
            print(e)


def make_q_parser(command_parser):
    query_parser = command_parser.add_parser(
        "query", help="Query one of the databases, if it exists"
    )

    query_parser.add_argument(
        "table", help="The table to query", choices=[x.__name__ for x in tables]
    )

    query_parser.add_argument(
        "-q",
        metavar="query",
        type=str,
        dest="params",
        action="append",
        help="Add a query. These should be in the form: param(comp)val\n comp is one of =,<,>,<=,>=",
    )
    query_parser.add_argument(
        "-u",
        "--update",
        dest="update",
        action="store_true",
        help="Whether to sync the table with the server (only works for Fits files for now)",
    )
    query_parser.set_defaults(func=parse_q)
