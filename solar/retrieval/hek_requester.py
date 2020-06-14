import requests
from datetime import datetime, timedelta
from requests.exceptions import HTTPError
import json
import concurrent.futures as cf
from solar.database.tables import Solar_Event
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

    def __init__(self, start_time, end_time, **kwargs):

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

    def break_into_intervals(self):
        interval = timedelta(days=60)
        current_time = self.start_time
        while current_time < self.end_time:
            next_time = current_time + interval
            if next_time < self.end_time:
                self.time_intervals.append((current_time, next_time))
            else:
                self.time_intervals.append((current_time, self.end_time))
            current_time = next_time

    def request_one_interval(self, start_time, end_time):
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
            print(f"Successfully retrieved events")
            json_data = json.loads(response.text)
            with Hek_Request.event_adder_lock:
                print(
                    "Acquiring lock with time interval {} -- {}".format(
                        start_time, end_time
                    )
                )
                self.events.extend(
                    [Solar_Event.from_hek(x, source="HEK") for x in json_data["result"]]
                )
                print(
                    "Releasing lock with time interval {} -- {}".format(
                        start_time, end_time
                    )
                )
                print(f"In thisiteration there are {len(self.events)}")

    def request(self):
        ret = []
        self.break_into_intervals()
        with cf.ThreadPoolExecutor(max_workers=5) as executor:
            ret = [
                executor.submit(self.request_one_interval, *interval)
                for interval in self.time_intervals
            ]
            for _ in tqdm(cf.as_completed(ret)):
                pass

    def print_to_file(self, filename="data.json"):
        with open(filename, "w") as f:
            print(f"Writing results to {filename}")
            f.write(json.dumps([e._asdict() for e in self.events], indent=4))

    def get_events(self):
        return self.events


def solar_requester_wrapper(start_time, end_time):
    s = Hek_Request(["cj"], start_time, end_time)
    s.request()
    s.save_to_database("test.db")
    return (s.events, s.found_count)


if __name__ == "__main__":
    h = Hek_Request("2010-06-01T00:00:00", "2011-06-10T00:00:00", event_types=["cj"])
    h.request()
    h.save_to_database()
