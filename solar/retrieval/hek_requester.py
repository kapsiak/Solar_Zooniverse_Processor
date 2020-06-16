from __future__ import annotations
from typing import List, Dict, Any
import requests
from datetime import datetime, timedelta
from requests.exceptions import HTTPError
import json
import concurrent.futures as cf
from solar.database import Solar_Event
from solar.retrieval.attribute import Attribute as Att
from solar.common.config import Config
from threading import Lock
from tqdm import tqdm


class Hek_Request:
    """
    Encapsulates a request to the Hek system
    """

    base_url = "http://www.lmsal.com/hek/her"
    attribute_list = []
    event_adder_lock = Lock()

    def __init__(self, start_time: str, end_time: str, **kwargs) -> None:
        """
        Initialize the request

        :param start_time: The time to start the search
        :type start_time: str
        :param end_time: The time to end the search
        :type end_time: str
        :param kwargs: kwargs to pass to the hek quer;w
        :type kwargs: Any
        :return: None
        :rtype: None
        """

        self.x1 = Att("x1", kwargs.get("x1", -1200))
        self.x2 = Att("x2", kwargs.get("x2", 1200))
        self.y1 = Att("y1", kwargs.get("y1", -1200))
        self.y2 = Att("y2", kwargs.get("y2", 1200))
        self.event_types = Att("event_type", kwargs.get("event_types", ["cj"]))
        self.channel = Att("channel", kwargs.get("channel", 304), "obs_channelid")
        self.coord_sys = Att(
            "coord_sys", kwargs.get("coord_sys", "helioprojective"), "event_coordsys"
        )
        self.start_time = datetime.strptime(start_time, Config["time_format_hek"])
        self.end_time = datetime.strptime(end_time, Config["time_format_hek"])
        self.cmd = Att("cmd", "search")
        self.use_json = Att("cosec", 2)
        self.command_type = Att("type", "column")
        self.other = [Att(x, kwargs[x]) for x in kwargs]

        self.time_intervals = []

        self.found_count = 0

        self.events = []

    def break_into_intervals(self, days: int = 60) -> None:
        """
        Break the time interval into subintervals, to avoid reaching the HEK response limit

        :param days: Interval length in days, defaults to 60
        :type days: int, optional
        :return: None
        :rtype: None
        """
        interval = timedelta(days=days)
        current_time = self.start_time
        while current_time < self.end_time:
            next_time = current_time + interval
            if next_time < self.end_time:
                self.time_intervals.append((current_time, next_time))
            else:
                self.time_intervals.append((current_time, self.end_time))
            current_time = next_time

    def request_one_interval(self, start_time: datetime.datetime, end_time: datetime.datetime) -> None:
        """
        Make a request to the HEK server for a single time interval

        :param start_time: Start time
        :type start_time: datetime.datetime
        :param end_time: End time
        :type end_time: datetime.datetime
        :return: None   
        :rtype: None
        """
        to_pass = {
            p.query_name: p.get_value()
            for p in [
                self.use_json,
                self.cmd,
                self.command_type,
                self.event_types,
                Att("start_time", start_time, "event_starttime"),
                Att("end_time", end_time, "event_endtime"),
                self.coord_sys,
                self.x1,
                self.x2,
                self.y1,
                self.y2,
                self.channel,
                *self.other,
            ]
        }
        try:
            response = requests.get(Hek_Request.base_url, params=to_pass)
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # Python 3.6
        except Exception as err:
            print(f"Other error occurred: {err}")  # Python 3.6
        else:
            #print(f"Successfully retrieved events")
            json_data = json.loads(response.text)
            with Hek_Request.event_adder_lock:
                events = [Solar_Event.from_hek(x, source="HEK")  for x in json_data["result"]]
                for e in events:
                    if not e in self.events:
                        self.events.append(e)
            #print(f"In thisiteration there are {len(self.events)}")

    def request(self) -> None:
        """
        Request all time intervals

        :return: None
        :rtype: None
        """
        self.break_into_intervals()
        with cf.ThreadPoolExecutor(max_workers=5) as executor:
            ret = [
                    executor.submit(self.request_one_interval, *interval)
                    for interval in self.time_intervals
                ]
            for _ in tqdm(
                cf.as_completed(ret),
                total=len(self.time_intervals),
                desc="Requesting Events from HEK"
            ):
                pass
        print(f"Found {len(self.events)} new events")
        if len(self.events) == 0:
            print(":(")

    def get_events(self) -> List[Solar_Event]:
        """
        Return a list of the found events

        :return: List of events found by the hek search
        :rtype: List[Solar_Event]
        """
        return self.events

    def save_events(self) -> None:
        for e in self.events:
            try:
                e.save()
            except IntegrityError as e:
                print(f"Could not save: {e}")
