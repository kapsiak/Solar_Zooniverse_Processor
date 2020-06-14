import requests
from datetime import datetime
from requests.exceptions import HTTPError
import concurrent.futures
import json
import solar.database.utils as db
from solar.database.tables import Solar_Event
from solar.retrieval.attribute import Attribute as Att


class Hek_Request:
    """
    Encapsulates a request to the Hek system
    """

    base_url = "http://www.lmsal.com/hek/her"
    attribute_list = []

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
        self.start_time = Att("start_time", start_time, "event_starttime")
        self.end_time = Att("end_time", end_time, "event_endtime")
        self.cmd = Att("cmd", "search")
        self.use_json = Att("cosec", 2)
        self.command_type = Att("type", "column")
        self.other = [Att(x, kwargs[x]) for x in kwargs]

        self.reponse = None
        self.json_data = None
        self.found_count = 0

        self.events = []

        self.response = None

    def request(self):
        to_pass = {
            p.query_name: p.get_value()
            for p in [
                self.use_json,
                self.cmd,
                self.command_type,
                self.event_types,
                self.start_time,
                self.end_time,
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
            self.response = requests.get(Hek_Request.base_url, params=to_pass)
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # Python 3.6
        except Exception as err:
            print(f"Other error occurred: {err}")  # Python 3.6
        else:
            print(f"Successfully retrieved events")
            self.json_data = json.loads(self.response.text)
            self.events = [
                Solar_Event.new(x, source="HEK") for x in self.json_data["result"]
            ]

    def print_to_file(self, filename="data.json"):
        with open(filename, "w") as f:
            print(f"Writing results to {filename}")
            f.write(json.dumps([e._asdict() for e in self.events], indent=4))

    def save_to_database(self):
        with db.database:
            for e in self.events:
                if not Solar_Event.select().where(Solar_Event.event_id == e.event_id):
                    e.save()


def solar_requester_wrapper(start_time, end_time):
    s = Hek_Request(["cj"], start_time, end_time)
    s.request()
    s.save_to_database("test.db")
    return (s.events, s.found_count)


if __name__ == "__main__":
    h = Hek_Request("2010-06-01T00:00:00", "2011-06-10T00:00:00", event_types=["cj"])
    h.request()
    h.save_to_database()
