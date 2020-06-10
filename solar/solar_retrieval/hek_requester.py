import requests
from datetime import datetime
from requests.exceptions import HTTPError
import concurrent.futures
import json
from solar.common.solar_event import Solar_Event
import solar.solar_database.database as sd
from solar.solar_database import database_name
import sqlite3

class Hek_Request:
    base_url = "http://www.lmsal.com/hek/her"
    time_format = "%Y-%m-%dT%H:%M:%S"

    def __init__(
        self, start_time, end_time, event_types=['cj'], x1=-1200, x2=1200, y1=-1200, y2=1200
    ):
        self.event_types = event_types
        self.query_type = 2
        self.start_time = datetime.strptime(start_time, self.time_format)
        self.end_time = datetime.strptime(end_time, self.time_format)
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.channel = 304

        self.coord_sys = "helioprojective"

        self.reponse = None
        self.data_json = None

        self.found_count = 0

        self.events = []

    def request(self):
        try:
            self.response = requests.get(
                Hek_Request.base_url,
                params={
                    "cosec": self.query_type,
                    "obs_channelid": self.channel,
                    "cmd": "search",
                    "type": "column",
                    "event_type": ",".join(self.event_types),
                    "event_starttime": self.start_time.strftime(
                        Hek_Request.time_format
                    ),
                    "event_endtime": self.end_time.strftime(Hek_Request.time_format),
                    "event_coordsys": self.coord_sys,
                    "x1": self.x1,
                    "y1": self.y1,
                    "x2": self.x2,
                    "y2": self.y2,
                    "result_limit": 1000,
                },
            )
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # Python 3.6
        except Exception as err:
            print(f"Other error occurred: {err}")  # Python 3.6
        else:
            print(
                f"Successfully retrieved events {self.event_types} "
                f"from times {self.start_time.strftime(self.time_format)}"
                f" to {self.start_time.strftime(self.time_format)} "
            )
            self.data_json = json.loads(json.dumps(self.response.json()))
            with open('temp.json', 'w') as f:
                f.write(json.dumps(self.data_json))

            for event in self.data_json["result"]:
                self.events.append(
                    Solar_Event(
                        sol=event["SOL_standard"],
                        start_time=event["event_starttime"],
                        end_time=event["event_endtime"],
                        x_min=event["boundbox_c1ll"],
                        x_max=event["boundbox_c1ur"],
                        y_min=event["boundbox_c2ll"],
                        y_max=event["boundbox_c2ur"],
                        hgc_x=event["hgc_x"],
                        hgc_y=event["hgc_y"],
                        instrument = event["obs_instrument"],
                        event_id=event["SOL_standard"]
                    )
                )
            self.found = len(self.events)
            print("Found: {} results".format(self.found))

    def print_to_file(self, filename="data.json"):
        with open(filename, "w") as f:
            print(f"Writing results to {filename}")
            f.write(json.dumps([e._asdict() for e in all_events], indent=4))

    def save_to_database(self,connection):
        sd.insert_all_events(connection,self.events)
            
        


def solar_requester_wrapper(start_time, end_time):
    s = Hek_Request(["cj"], start_time, end_time)
    s.request()
    s.save_to_database('test.db')
    return (s.events, s.found_count)


if __name__ == "__main__":
    filename = "data.json"
    total_found = 0
    all_events = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(
                solar_requester_wrapper,
                f"{date}-01-01T00:00:00",
                f"{date+1}-01-01T00:00:00",
            )
            for date in range(2007, 2010)
        ]
        for future in concurrent.futures.as_completed(futures):
            events, found = future.result()
            all_events.extend(events)
            total_found += found
    with open(filename, "w") as f:
        print(f"Writing results to {filename}")
        f.write(json.dumps([e._asdict() for e in all_events], indent=4, sort_keys=True))
    print(f"Found a total of {total_found} recorded events")
