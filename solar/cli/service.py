from solar.service.hek import Hek_Service
from solar.service.cutout import Cutout_Service
import re
import peewee as pw

query_re = re.compile("([a-zA-Z1-9_]+)\s*=\s*([a-zA-Z1-9_-]+)")


def parse_cutout(param_dict, action, save_data=False, save_request=False):
    c = Cutout_Service(**param_dict)
    if action == "submit":
        c.submit_request()
    elif action == "fetch":
        c.fetch_data()

    if c.data and save_data:
        for x in c.data:
            try:
                x.save()
            except pw.IntegrityError as e:
                print(e)
    if save_request:
        x.save_request()


def parse_hek(param_dict, action, save_data=False, save_request=False):
    h = Hek_Service(**param_dict)
    h.submit_request()
    events = h.data
    for x in events:
        print(x)
    if save_data:
        for x in events:
            try:
                x.save()
            except pw.IntegrityError as e:
                print(e)


def parse_s(args):
    params = args.params if args.params else []
    query_dict = {
        param: val for param, val in [query_re.search(q).groups() for q in params]
    }
    serv = args.service
    if serv == "hek":
        parse_hek(query_dict, 's')
    elif serv == "cutout":
        parse_cutout(query_dict)


def make_s_parser(command_parser):
    service_parser = command_parser.add_parser(
        "service", help="Submit a request to a some service"
    )

    service_parser.add_argument(
        "service",
        help="The service to submit the request to",
        choices=["hek", "cutout"],
    )

    group1 = service_parser.add_mutually_exclusive_group()
    group1.add_argument(
        "-q",
        metavar="query",
        type=str,
        dest="params",
        action="append",
        help="Queries of the form: param=val",
    )
    group1.add_argument(
        "-i",
        "--identity",
        metavar="identity",
        type=str,
        dest="identity",
        help="An identifier for an existiting request",
    )

    group2 = service_parser.add_mutually_exclusive_group(required=True)
    group2.add_argument(
        "-s", "--submit", action="store_true", help="Submit a request to the service"
    )
    group2.add_argument(
        "-f",
        "--fetch",
        action="store_true",
        help="Attempt to fetch data from a request. If the request has not been submitted, this command will first submit the request",
    )

    service_parser.add_argument(
        "-w", "--save-data", action="store_true", help="Save the data from the request"
    )
    service_parser.add_argument(
        "-r", "--save-request", action="store_true", help="Save the request itself"
    )

    service_parser.set_defaults(func=parse_s)
