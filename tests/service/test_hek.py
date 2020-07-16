from solar.service.hek import Hek_Service
from solar.database.tables.solar_event import Solar_Event
from solar.database.tables.service_request import Service_Request
import unittest
from unittest import mock
from tests.utils import test_db, mock_get_json
from pathlib import Path
import json
from datetime import datetime, timedelta
from solar.common.config import Config


def load_responses(folder="resp"):
    test_dir = Path(__file__).parent / f"{folder}/"
    resp_list = []
    for test_file in test_dir.glob("*.txt"):
        with open(test_file, "r") as f:
            json_data = ""
            params = f.readline().strip()
            params = json.loads(params)["params"]
            for line in f:
                json_data += line
            json_data = json.loads(json_data)
        resp_list.append([params, json_data])
    return resp_list


class TestHek(unittest.TestCase):
    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_kwargs(self):
        param_dict = dict(
            param1=1, param2=1.1, param3="hello", param4=["x", "y"], param5=[1, 2, 3]
        )
        hek = Hek_Service(**param_dict)
        for x in param_dict:
            self.assertEqual(hek[x], param_dict[x])

    @test_db()
    @mock.patch("requests.get", side_effect=mock_get_json(load_responses()))
    def test_request(self, mock_get):
        x, y = ("2010-06-01T00:00:00", "2010-07-01T00:00:00")
        hek = Hek_Service(event_starttime=x, event_endtime=y)
        hek.submit_request()
        self.assertEqual(len(hek.data), 8)
        event1 = hek.data[0]
        self.assertEqual(event1.sol_standard, "SOL2010-06-04T09:21:47L246C049")

    @test_db()
    def test_save_requests(self):
        h = Hek_Service()
        events = [
            Solar_Event(event_id="1"),
            Solar_Event(event_id="123123"),
            Solar_Event(event_id="12031mmjdd"),
            Solar_Event(event_id="asdfnadfsoos"),
        ]

        h._data = events
        self.assertEqual(len(h._data), 4)

        h.save_data()
        self.assertEqual(len(Solar_Event.select()), 4)

        for x, y in zip(events, Solar_Event.select()):
            self.assertEqual(x.event_id, y.event_id)

        h.save_data()
        self.assertEqual(len(Solar_Event.select()), 4)

        for x, y in zip(events, Solar_Event.select()):
            self.assertEqual(x.event_id, y.event_id)

    @test_db()
    def test_save_request(self):
        base = datetime.today()
        total = 1
        date_list = [base - timedelta(days=120 * x) for x in range(total)]
        requests = [
            Hek_Service(
                event_starttime=x.strftime(Config.time_format.hek),
                event_endtime=y.strftime(Config.time_format.hek),
            )
            for x in date_list
            for y in date_list
        ]
        for x in requests:
            x.save_request()
        self.assertEqual(
            Service_Request.select().where(Service_Request.service_type == "hek"),
            total * total,
        )

        for x in requests:
            x.save_request()
        self.assertEqual(
            Service_Request.select().where(Service_Request.service_type == "hek"),
            total * total,
        )

        for x, y in zip(
            requests,
            Service_Request.select().where(Service_Request.service_type == "hek"),
        ):
            self.assertEqual(x.start_time, y["event_starttime"])


if __name__ == "__main__":
    d = load_responses()
    t = TestHek()
    t.test_request()
