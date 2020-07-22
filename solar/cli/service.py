from solar.service.hek import Hek_Service
from solar.service.cutout import Cutout_Service
from solar.database.tables.service_request import Service_Request
from solar.database.tables.hek_event import Hek_Event
import re
import peewee as pw

query_re = re.compile("([a-zA-Z1-9_]+)\s*=\s*([a-zA-Z1-9_-]+)")


def grab_save(req, action, save_data, save_request):
    if action == "submit":
        req.submit_request()
    elif action == "fetch":
        req.fetch_data()
    if req.data and save_data:
        for x in req.data:
            try:
                x.save()
            except pw.IntegrityError as e:
                pass
    if save_request:
        req.save_request()


def parse_cutout_exist(search, action, save_data=False, save_request=False):
    cut = Service_Request.select().where(
        (Service_Request.service_type == "cutout")
        & ((Service_Request.id % search) | (Service_Request.job_id % f"%{search}%"))
    )
    if not cut:
        print("Could not find any requests matching the search")
        return None
    elif len(cut) > 1:
        print("I found too many requests with this search, please try to narrow it")
        for x in cut:
            print(x)
        return None
    c = Cutout_Service._from_model(cut.get())
    print("I will use the request")
    print(c)
    grab_save(c, action, save_data, save_request)


def parse_cutout_event(search, action, save_data=False, save_request=False):
    event = Hek_Event.select().where(
        (Hek_Event.id % search)
        | (Hek_Event.event_id.contains(search))
        | (Hek_Event.sol_standard % f"%{search}%")
    )
    if not event:
        print("Could not find any requests matching the search")
        return None
    elif len(event) > 1:
        print("I found too many requests with this search, please try to narrow it")
        for x in event:
            print(x)
        return None
    c = Cutout_Service._from_event(event.get())
    print("I will use the request")
    print(c)
    grab_save(c, action, save_data, save_request)


def parse_hek_exist(search, action, save_data=False, save_request=False):
    hek = Service_Request.select().where(
        (Service_Request.service_type == "hek")
        & ((Service_Request.id % search) | (Service_Request.job_id % f"%{search}%"))
    )
    if not hek:
        print("Could not find any requests matching the search")
        return None
    elif len(hek) > 1:
        print("I found too many requests with this search, please try to narrow it")
        for x in hek:
            print(x)
        return None
    h = Hek_Service._from_model(hek.get())
    print("I will use the request")
    print(h)
    grab_save(h, action, save_data, save_request)


def parse_cutout_params(param_dict, action, save_data=False, save_request=False):
    c = Cutout_Service(**param_dict)
    grab_save(c, action, save_data, save_request)


def parse_hek_params(param_dict, action, save_data=False, save_request=False):
    h = Hek_Service(**param_dict)
    grab_save(h, action, save_data, save_request)


def parse_s(args):
    serv = args.service
    act = "fetch" if args.fetch else "submit"
    save_dat = args.save_data
    save_req = args.save_request
    event = args.event if args.event else None
    if args.search:
        search_pattern = args.search
        if serv == "hek":
            parse_hek_exist(
                search_pattern, act, save_data=save_dat, save_request=save_req
            )
        elif serv == "cutout":
            if not event:
                parse_cutout_exist(
                    search_pattern, act, save_data=save_dat, save_request=save_req
                )
            else:
                parse_cutout_event(
                    search_pattern, act, save_data=save_dat, save_request=save_req
                )

    else:
        params = args.params if args.params else []
        query_dict = {
            param: val for param, val in [query_re.search(q).groups() for q in params]
        }
        if serv == "hek":
            parse_hek_params(query_dict, act, save_data=save_dat, save_request=save_req)
        elif serv == "cutout":
            parse_cutout_params(
                query_dict, act, save_data=save_dat, save_request=save_req
            )


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
        "--search",
        metavar="search",
        type=str,
        dest="search",
        help="An identifier for an existiting request",
    )

    group2 = service_parser.add_mutually_exclusive_group(required=True)
    group2.add_argument(
        "-s",
        "--submit",
        action="store_true",
        help="Submit a request to the service. Depending on the service this may or may not be a different action than a data fetch.",
    )
    group2.add_argument(
        "-f",
        "--fetch",
        action="store_true",
        help="Attempt to fetch data from a request. If the request has not been submitted, this command will first submit the request.\n Note that this may take some time and will block.",
    )

    service_parser.add_argument(
        "-w", "--save-data", action="store_true", help="Save the data from the request"
    )
    service_parser.add_argument(
        "-r",
        "--save-request",
        action="store_true",
        help="Save the request itself",
        default=True,
    )

    service_parser.add_argument(
        "--event",
        action="store_true",
        help="If submitting a cutout request, look for an existing solar event matching the parameter (as opposed to a cutout request), and create a cutout request using that event",
    )

    service_parser.set_defaults(func=parse_s)
