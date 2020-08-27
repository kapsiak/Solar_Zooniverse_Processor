from __future__ import annotations
from typing import List, Dict, Any
import requests
from datetime import datetime, timedelta
from requests.exceptions import HTTPError
import json
import concurrent.futures as cf
from solar.database.tables.hek_event import Hek_Event
from solar.database.tables.service_request import Service_Request, Service_Parameter
from solar.service.attribute import Attribute as Att
from solar.common.config import Config
from threading import Lock
from tqdm import tqdm
from solar.service.request import Base_Service
import peewee as pw
from solar.service.utils import build_from_defaults
from solar.common.printing import chat


class Hek_Service(Base_Service):
    """
    Encapsulates a request to the Hek system
    """

    # API url for the hek service
    base_url = "http://www.lmsal.com/hek/her"

    service_type = "hek"

    # Lock to prevent data races
    event_adder_lock = Lock()

    def __init__(self, *args, **kwargs):
        """
        Initialize the request.
        The kwargs correspond exactly to the keywords described in `HEK API Reference
        <http://solar.stanford.edu/hekwiki/ApplicationProgrammingInterface?action=print>`_

        :param kwargs: kwargs to pass to the hek query
        :type kwargs: Any
        """

        self.service_request_id = None
        self.job_id = None

        start = "2010-06-01T00:00:00"
        end = "2010-07-01T00:00:00"

        # Default attributes
        x1 = Att("x1", -1200)
        x2 = Att("x2", 1200)
        y1 = Att("y1", -1200)
        y2 = Att("y2", 1200)
        event_types = Att("event_type", ["cj"])
        channel = Att("obs_channelid", 304)
        coord_sys = Att("event_coordsys", "helioprojective")
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

        # Temporary object to store user parameters
        temp = []
        temp.extend(args)
        temp.extend([Att(key, kwargs[key]) for key in kwargs])

        # Construct the final parameter list by replacing defaults with user defined values
        self.params = build_from_defaults(defaults, temp)

        self.start_time = [x for x in self.params if x.name == "event_starttime"][
            0
        ].value
        self.end_time = [x for x in self.params if x.name == "event_endtime"][0].value

        self.found_count = 0

        self._data = []

        self.status = "unsubmitted"

        self.for_testing_data = {"result": []}

    def __parse_attributes(self, params, **kwargs):
        """
        Parse attributes and return a dictionary that can be passed to a request object

        :param params: The params to parse
        :type params: List[Attribute]
        :param kwargs: Additional key value pairs. 
        :rtype: Dict[str,Any]
        """
        other = [Att(key, kwargs[key]) for key in kwargs]
        new_params = build_from_defaults(params, other)
        return {att.name: att.value for att in new_params}

    def __break_into_intervals(self, days=60):
        """
        Break the time interval into subintervals, to avoid reaching the HEK response limit

        :param days: Interval length in days, defaults to 60
        :type days: int, optional
        :return: None
        :rtype: None
        """

        start = datetime.strptime(self.start_time, Config.time_format.hek)
        end = datetime.strptime(self.end_time, Config.time_format.hek)

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
        return [
            (x.strftime(Config.time_format.hek), y.strftime(Config.time_format.hek))
            for x, y in ret
        ]

    def _request_one_interval(self, start_time, end_time):
        """
        Make a request to the HEK server for a single time interval

        :param start_time: Start time
        :type start_time: datetime.datetime
        :param end_time: End time
        :type end_time: datetime.datetime
        :return: None   
        :rtype: None
        """
        to_pass = self.__parse_attributes(
            self.params, event_starttime=start_time, event_endtime=end_time
        )
        try:
            response = requests.get(Hek_Service.base_url, params=to_pass)
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # Python 3.6
        except Exception as err:
            print(f"Other error occurred: {err}")  # Python 3.6
        else:
            json_data = response.json()
            with Hek_Service.event_adder_lock:
                events = [
                    Hek_Event.from_hek(x, source="HEK") for x in json_data["result"]
                ]
                self.for_testing_data["result"].extend(json_data["result"])
                for e in events:
                    if not e in self._data:
                        self.data.append(e)
            self.status = "completed"

    @property
    def data(self):
        return self._data

    def submit_request(self):
        """
        Submit a request to the HEK service.
        """
        intervals = self.__break_into_intervals()
        with cf.ThreadPoolExecutor(max_workers=5) as executor:
            ret = [
                executor.submit(self._request_one_interval, *interval)
                for interval in intervals
            ]
            for _ in tqdm(
                cf.as_completed(ret),
                total=len(intervals),
                desc="Requesting Events from HEK",
            ):
                pass

        print(f"Found {len(self._data)} new events")

    def fetch_data(self):
        """
        Return a list of the found events

        :return: List of events found by the hek search
        .. py:module:: solar.database.tables.hek_event
        :rtype: List[:class:`Hek_Event`]
        """
        return self.data

    def save_data(self):
        """
        Save the data found from the request to the database
        """
        self._data = [
            e
            if Hek_Event.select().where(Hek_Event.event_id == e.event_id).count() == 0
            else Hek_Event.select().where(Hek_Event.event_id == e.event_id).get()
            for e in self._data
        ]
        for e in self.data:
            try:
                e.save()
            except pw.IntegrityError as err:
                print(err)
                chat(
                    f"Looks like the event {e} is already in the database, so I am replacing it with the existing one"
                )

    @staticmethod
    def _from_model(serv_obj):
        """Function _from_model: Create a Hek_Service from an existing model
             
        :param serv_obj: Service_Request object (from table)
        :type serv_obj: Service_Request
        :returns: The created request
        :type return: Hek_Service
        """
        att_list = [Att.from_model(x) for x in serv_obj.parameters]
        h = Hek_Service(*att_list)
        h.status = serv_obj.status
        return h

    def __getitem__(self, key):
        return [x for x in self.params if x.name == key][0].value


if __name__ == "__main__":
    from solar.database import create_tables

    create_tables()
    x, y = ("2010-06-01T00:00:00", "2010-07-01T00:00:00")
    h = Hek_Service(event_starttime=x, event_endtime=y)
    h.submit_request()
    with open("hek_1.txt", "w") as f:
        f.write(json.dumps({"params": {a.name: a.value for a in h.params}}))
        f.write("\n")
        f.write(json.dumps(h.for_testing_data, indent=4))
