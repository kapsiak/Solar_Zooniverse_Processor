from __future__ import annotations
from typing import List, Dict, Any
import requests
from datetime import datetime, timedelta
from requests.exceptions import HTTPError
import json
import concurrent.futures as cf
from solar.database import Solar_Event, Service_Request,Service_Parameter
from solar.retrieval.attribute import Attribute as Att
from solar.common.config import Config
from threading import Lock
from tqdm import tqdm
from solar.retrieval.request import Base_Service
import peewee as pw


def build_from_defaults(default_list, new_list):
    ret = []
    for i in default_list:
        search = [x for x in new_list if x.name == i.name]
        if search:
            ret.append(search[0])
        else:
            ret.append(i)
    return ret

class Hek_Service(Base_Service):
    """
    Encapsulates a request to the Hek system
    """

    base_url = "http://www.lmsal.com/hek/her"
    attribute_list = []
    event_adder_lock = Lock()

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the request

        :param start_time: The time to start the search
        :type start_time: str
        :param end_time: The time to end the search
        :type end_time: str
        :param kwargs: kwargs to pass to the hek query
        :type kwargs: Any
        :return: None
        :rtype: None
        """
        start = "2010-06-01T00:00:00"
        end = "2010-07-01T00:00:00"

        x1 = Att("x1", kwargs.get("x1", -1200))
        x2 = Att("x2", kwargs.get("x2", 1200))
        y1 = Att("y1", kwargs.get("y1", -1200))
        y2 = Att("y2", kwargs.get("y2", 1200))
        event_types = Att("event_type", kwargs.get("event_types", ["cj"]))
        channel = Att("obs_channelid", kwargs.get("channel", 304))
        coord_sys = Att("event_coordsys", kwargs.get("coord_sys", "helioprojective"))
        start_time = Att("event_starttime", start)
        end_time = Att("event_endtime", end)
        cmd = Att("cmd", "search")
        use_json = Att("cosec", 2)
        command_type = Att("type", "column")

        defaults = [
            x1,
            x2,
            y1,
            y2,
            event_types,
            channel,
            coord_sys,
            start_time,
            end_time,
            cmd,
            use_json,
            command_type,
        ]

        temp = []
        temp.extend(args)
        temp.extend([Att(key, kwargs[key]) for key in kwargs])
        self.params = build_from_defaults(defaults,temp)


        self.start_time = [x for x in self.params if x.name == "event_starttime"][0].value
        self.end_time = [x for x in self.params if x.name == "event_endtime"][0].value

        self.found_count = 0

        self._data = []

        self.request_status = "unsubmitted"

    def __parse_attributes(self, params, **kwargs):
        other = [Att(key, kwargs[key]) for key in kwargs]
        new_params = build_from_defaults(params,other)
        return {att.name: att.value for att in new_params}

    def __break_into_intervals(self, days: int = 60) -> None:
        """
        Break the time interval into subintervals, to avoid reaching the HEK response limit

        :param days: Interval length in days, defaults to 60
        :type days: int, optional
        :return: None
        :rtype: None
        """
        start = datetime.strptime(self.start_time, Config["time_format_hek"])
        end = datetime.strptime(self.end_time, Config["time_format_hek"])

        interval = timedelta(days=days)
        ret = []

        current_time = start
        while current_time < end:
            next_time = current_time + interval
            if next_time < end:
                ret.append((current_time, next_time))
            else:
                ret.append((current_time, end))
            current_time = next_time
        return [(x.strftime(Config["time_format_hek"]),
                y.strftime(Config["time_format_hek"]))
                for x,y in ret
            ]


    def _request_one_interval(
        self, start_time: datetime.datetime, end_time: datetime.datetime
    ) -> None:
        """
        Make a request to the HEK server for a single time interval

        :param start_time: Start time
        :type start_time: datetime.datetime
        :param end_time: End time
        :type end_time: datetime.datetime
        :return: None   
        :rtype: None
        """
        to_pass = self.__parse_attributes(self.params, event_starttime= start_time, event_endtime = end_time)
        try:
            response = requests.get(Hek_Service.base_url, params=to_pass)
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # Python 3.6
        except Exception as err:
            print(f"Other error occurred: {err}")  # Python 3.6
        else:
            # print(f"Successfully retrieved events")
            json_data = json.loads(response.text)
            with open("test.json", "w") as f:
                f.write(json.dumps(json_data, indent=4))
            with Hek_Service.event_adder_lock:
                events = [
                    Solar_Event.from_hek(x, source="HEK") for x in json_data["result"]
                ]
                for e in events:
                    if not e in self._data:
                        self.data.append(e)
            self.status = 'completed'
    @property
    def data(self):
        return self._data

    def submit_request(self) -> None:
        """
        Request all time intervals

        :return: None
        :rtype: None
        """
        intervals = self._break_into_intervals()
        with cf.ThreadPoolExecutor(max_workers=5) as executor:
            ret = [
                executor.submit(self._request_one_interval, *interval)
                for interval in intervals
            ]
            for _ in tqdm(
                cf.as_completed(ret),
                total=len(self.time_intervals),
                desc="Requesting Events from HEK",
            ):
                pass

        print(f"Found {len(self.events)} new events")

    def fetch_data(self) -> List[Solar_Event]:
        """
        Return a list of the found events

        :return: List of events found by the hek search
        :rtype: List[Solar_Event]
        """
        return self.data

    def save_data(self) -> None:
        for e in self.data:
            try:
                e.save()
            except pw.IntegrityError as err:
                print(f"Could not save: {e} : {err}")

    def save_request(self):
        s = Service_Request(
                event = None,
                service_type = 'hek',
                status = self.status,
                job_id = None
                )
        print(s)
        for p in self.params:
            print(p)
        params = [Service_Parameter(
            service_request = s,
            key = a.name,
            val = a.get_value(),
            desc = a.description
            ) for a in self.params]
        s.save()
        for p in params:
            p.save()

    
    @staticmethod
    def _from_model(serv_obj):
        att_list = [Att.from_model(x) for x in serv_obj.parameters]
        h = Hek_Service(*att_list)
        h.status = serv_obj.status
        return h



if __name__ == "__main__":
    from solar.database import create_tables
    create_tables()
    h = Hek_Service()
    x,y =('2010-06-01T00:00:00', '2010-07-01T00:00:00')
    h._request_one_interval(x,y) 
    h.save_data()
    h.save_request()
    mod = Service_Request.get()
    print(mod)
    new = Hek_Service._from_model(mod)
    for param in new.params:
        print(param)
