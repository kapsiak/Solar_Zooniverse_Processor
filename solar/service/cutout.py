from __future__ import annotations
from typing import List, Dict, Any
import requests
from datetime import datetime
from requests.exceptions import HTTPError
import re
from pathlib import Path
import time
from solar.common.config import Config
from solar.database.utils import dbformat
from solar.database.tables.solar_event import Solar_Event
from solar.database.tables.fits_file import Fits_File
from solar.database.tables.service_request import Service_Parameter, Service_Request
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import tqdm
from peewee import DoesNotExist
from .attribute import Attribute as Att
from .utils import build_from_defaults
from .request import Base_Service
import peewee as pw
from solar.common import chat


class Cutout_Service(Base_Service):

    # The base url for the ssw response, a response from this returns, most importatnyl, the job ID associated with this cuttout request
    base_api_url = "http://www.lmsal.com/cgi-ssw/ssw_service_track_fov.sh"
    data_response_url_template = "https://www.lmsal.com/solarsoft//archive/sdo/media/ssw/ssw_client/data/{ssw_id}/"
    delay_time = 60  # seconds

    @staticmethod
    def _from_event(event, strict=True):

        if strict:
            try:
                c = Service_Request.get(
                    Service_Request.event == event,
                    Service_Request.service_type == "cutout",
                )
                chat(f"I found a cutout request for event {event.__repr__()}")
                return Cutout_Service._from_model(c)
            except pw.DoesNotExist:
                pass
        chat("I could not find request matching this event, I will create a new one")
        to_pass = dict(
            xcen=event.hpc_x,
            ycen=event.hpc_y,
            fovx=abs(event.x_max - event.x_min),
            fovy=abs(event.y_max - event.y_min),
            notrack=1,
            starttime=event.start_time,
            endtime=event.end_time,
        )
        c = Cutout_Service(**to_pass)
        c.event = event
        return c

    @staticmethod
    def _from_model(mod):
        params = [Att.from_model(x) for x in mod.parameters]
        cut = Cutout_Service(*params)
        cut.event = mod.event
        cut.status = mod.status
        cut.service_request_id = mod.id
        cut.job_id = mod.job_id

        return cut

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize a cutout request. 

        Args may be attributes of the form: Attribute(name,value)
        Kwargs may be attributes in the form : name=value
        These two will produce equivalent searches
        

        :param event: The solar event the cutout request refers to
        :type event: Union[Solar_Event, str]
        :param allow_similar: Whether or not to allow similar requests to be made, defaults to False
        :type allow_similar: bool, optional
        :return: None
        :rtype: None
        """
        start = datetime.strptime("2010-06-01T00:00:00", Config.time_format.hek)
        end = datetime.strptime("2010-07-01T00:00:00", Config.time_format.hek)

        xcen = Att("xcen", kwargs.get("xcen", 0))
        ycen = Att("ycen", kwargs.get("ycen", 0))
        fovx = Att("fovx", kwargs.get("fovx", 100))
        fovy = Att("fovy", kwargs.get("fovy", 100))
        queue = Att("queue_job", kwargs.get("queue", 1))
        channel = Att("waves", kwargs.get("channel", 304))
        notrack = Att("notrack", kwargs.get("notrack", 1))
        start_time = Att("starttime", start, t_format=Config.time_format.hek)
        end_time = Att("endtime", end, t_format=Config.time_format.hek)
        cmd = Att("cmd", "search")
        use_json = Att("cosec", 2)
        command_type = Att("type", "column")

        defaults = [
            xcen,
            ycen,
            fovx,
            fovy,
            queue,
            notrack,
            start_time,
            end_time,
            channel,
        ]

        temp = []
        temp.extend(args)
        temp.extend(
            [Att(key, kwargs[key], t_format=Config.time_format.hek) for key in kwargs]
        )
        self.params = build_from_defaults(defaults, temp)
        for x in self.params:
            print(x._format)
        self.event = None

        self.service_request_id = None

        self.job_id = None  # The SSW job ID

        self.status = "unsubmitted"

        self._data = None  # The text from the response

    @property
    def data(self):
        return self._data

    def __parse_attributes(self, **kwargs):
        other = [
            Att(key, kwargs[key], t_format=Config.time_format.hek) for key in kwargs
        ]
        new_params = build_from_defaults(self.params, other)
        return {att.name: att.f_value() for att in new_params}

    def submit_request(self) -> None:
        """
        Make a request to the SSW server in order to begin processing.

        :return: None
        :rtype: None
        """
        if not self.job_id:
            try:
                response = requests.get(
                    Cutout_Service.base_api_url, params=self.__parse_attributes()
                )
            except HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")  # Python 3.6
            except Exception as err:
                print(f"Other error occurred: {err}")  # Python 3.6
            else:
                # print(f"Successfully submitted request ")
                self.job_id = re.search(
                    '<param name="JobID">(.*)</param>', response.text
                )[1]
        self.status = "submitted"

    def fetch_data(self, delay=None) -> None:
        """
        Attempt to fetch the data from the ssw_server.
        :return: None
        :rtype: None
        """
        data_response_url = Cutout_Service.data_response_url_template.format(
            ssw_id=self.job_id
        )
        data_acquired = False  # Have we been able to get the data_file list?

        delay_time = delay if delay else Cutout_Service.delay_time

        while not data_acquired:

            # In the below statements, we fetch the html from the data_response_url
            # We then check if the response contains the string "Per-Wave file lists", to determine
            # if the request has been processed
            try:
                data_response = requests.get(data_response_url)
            except HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")  # Python 3.6
            except Exception as err:
                print(f"Other error occurred: {err}")  # Python 3.6
            else:
                if re.search("Per-Wave file lists", data_response.text):
                    data_acquired = True
                else:
                    chat("Data not available")
                    time.sleep(delay_time)
                    chat(f"Attempting to fetch data from {data_response_url}")
        # print("Data now available")
        # Once the response has been processed we need to extract the list of fits files
        if data_acquired:
            self.status = "completed"
            fits_list_url = re.search('<p><a href="(.*)">.*</a>', data_response.text)[1]

            if not fits_list_url:
                # print(f"Looks like there are no cut out files available")
                return False

            # List_files_raw contains the pure text from the page listing the urls
            # We then split and extract the actial name
            try:
                list_files_raw = requests.get(data_response_url + fits_list_url).text
            except HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")  # Python 3.6
            except Exception as err:
                print(f"Other error occurred: {err}")  # Python 3.6
            else:
                file_list = list_files_raw.split("\n")
                file_list = [re.search(".*/(.*)$", x)[1] for x in file_list if x]
                self._data = self._as_fits(file_list)

    def save_data(self):
        pass

    def save_request(self):
        if self.status == "unsubmitted":
            chat("No reason to save an unsubmitted service request")
            return None

        if not self.service_request_id:
            try:
                req = Service_Request.get(
                    Service_Request.job_id == self.job_id,
                    Service_Request.service_type == "cutout",
                )
                chat(
                    (
                        "While saving this request, I found an existing request with a matching job id.\n"
                        "I am going to update that request instead"
                    )
                )
            except pw.DoesNotExist:
                chat(
                    ("I could not find any matching request. I am creating a new one.")
                )
                req = Service_Request.create(service_type="cutout", status=self.status)
                chat(f"The new request's ID is {req.id}")
            except Exception as e:
                print(f"Other error: {e}")

        else:
            try:
                chat("This request already has an id, I will try saving it to that")
                req = Service_Request.get_by_id(self.service_request_id)
            except pw.DoesNotExist:
                print(
                    f"Somehow this request has an invalid id: {self.service_request_id}  "
                    "I don't know what to do with this so I am bailing."
                )
                return None

            except Exception as e:
                print(f"Other error: {e}")
                return None

        self.service_request_id = req.id

        if self.event:
            req.event = self.event
        else:
            req.event = None

        req.service_type = "cutout"
        req.status = self.status

        req.job_id = self.job_id

        param_list = [p for p in req.parameters]
        my_params = [a.as_model(req) for a in self.params]

        new_list = []

        for param in my_params:
            search = [x for x in param_list if x.key == param.key]
            if not search:
                new_list.append(param)
            else:
                param.id = search[0].id
                new_list.append(param)

        req.save()
        for p in new_list:
            p.save()

    def _as_fits(self, file_list: List[str]) -> List[Fits_File]:
        """
        Use the fits file list to construct and insert fits_files into the database.
        Note that this does not download the files. That is done through the
        update_table command.

        :param file_list: A list of server_file_names
        :type file_list: List[str]
        :return: List of fits files (already inserted;w
        :rtype: List[Fits_File]
        """
        ret = []
        sol = self.event.sol_standard if self.event else "unknown"
        event_id = self.event.event_id if self.event else None
        req_id = self.service_request_id if self.service_request_id else None

        data_response_url = Cutout_Service.data_response_url_template.format(
            ssw_id=self.job_id
        )

        for fits_server_file in file_list:

            f = Fits_File(
                event=self.event,
                sol_standard=sol,
                ssw_cutout_id=self.job_id,
                server_file_name=fits_server_file,
                server_full_path=data_response_url + fits_server_file,
                file_name=fits_server_file,
                request_id=req_id,
            )
            f.file_path = Fits_File.make_path(f, event_id=event_id)
            print(f.file_path)
            ret.append(f)
        return ret


def c_fetch(c: Cutout_Service) -> Cutout_Service:
    """
    A wrapper function for processing cutout requests

    :param c: The request
    :type c: Cutout_Service
    :return: The request after executing both the request and fetch stages
    :rtype: Cutout_Service
    """
    c.fetch_data()
    c.save_request()
    return c


def multi_cutout(list_of_reqs: List[Cutout_Service]) -> List[Cutout_Service]:
    """
    A multithreaded cutout requester. 
    Accepts a list of cutout requests, processes them in paralle and then returns a list of the 
    processed requests

    WARNING: The order of the original list is not guaranteed to be preserved in the returned list

    :param list_of_reqs: List of requests to be processed
    :type list_of_reqs: List[Cutout_Service]
    :return: List of completed request
    :rtype: List[Cutout_Service]
    """
    with ThreadPoolExecutor(max_workers=20) as executor:
        total_jobs = len(list_of_reqs)
        completed = 0
        chat("Starting Requests")
        chat(
            f"Currently there are {completed} finished fetches and {total_jobs-completed} pending fetches",
            end="\r",
        )
        cmap = {executor.submit(c_fetch, c): c for c in list_of_reqs}
        ret = []

        for future in concurrent.futures.as_completed(cmap):
            ret.append(future.result())
            completed += 1
            chat(
                f"Currently there are {completed} finished fetches and {total_jobs-completed} pending fetches",
                end="\r",
            )
        chat("\nDone")
    return ret


if __name__ == "__main__":
    from solar.database import create_tables

    create_tables()
    x = Service_Request.get()
    c = Cutout_Service._from_model(x)
    for param in c.params:
        print(param)
    c.save_request()
    c.submit_request()
    c.fetch_data()
    c.save_request()
    print(c.data)
