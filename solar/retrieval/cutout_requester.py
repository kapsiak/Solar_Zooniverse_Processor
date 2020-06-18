from __future__ import annotations
from typing import List, Dict, Any
import requests
from datetime import datetime
from requests.exceptions import HTTPError
import re
from pathlib import Path
import time
from solar.common.config import Config
import solar.database.utils as dbs
from solar.database import Solar_Event, Fits_File, Service_Parameter, Service_Request
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import tqdm
from peewee import DoesNotExist
from .attributes import Attribute as Att
from .utils import build_from_defaults
from .requests import Base_Service


class Cutout_Service(Base_Service):

    # The base url for the ssw response, a response from this returns, most importatnyl, the job ID associated with this cuttout request
    base_api_url = "http://www.lmsal.com/cgi-ssw/ssw_service_track_fov.sh"
    data_response_url_template = "https://www.lmsal.com/solarsoft//archive/sdo/media/ssw/ssw_client/data/{ssw_id}/"
    repeat_time = 60  # seconds

    @static_method
    def _from_event(event):
        to_pass = dict(
            xcen=event.hpc_x,
            ycen=event.hpc_y,
            fovx=abs(self.event.x_max - self.event.x_min),
            fovy=abs(self.event.y_max - self.event.y_min),
            notrack=1,
            start=event.start_time,
            end=event.end_time,
        )
        return Cutout_Service(**to_pass)

    @staticmethod
    def _from_model(mod):
        if mod.event:
            return Cutout_Service._from_event(mod.event)

        params = [Att._from_model(x) for x in mod.parameters]
        cut = Cutout_Service(*params)
        cut.status = mod.status
        cut.job_id = mod.job_id

        return cut

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize a cutout request
todo
        :param event: The solar event the cutout request refers to
        :type event: Union[Solar_Event, str]
        :param allow_similar: Whether or not to allow similar requests to be made, defaults to False
        :type allow_similar: bool, optional
        :return: None
        :rtype: None
        """
        start = "2010-06-01T00:00:00"
        end = "2010-07-01T00:00:00"

        xcen = Att("xcen", kwargs.get("xcen", 0))
        ycen = Att("ycen", kwargs.get("ycen", 0))
        fovx = Att("fovx", kwargs.get("fovx", 100))
        fovy = Att("fovy", kwargs.get("fovy", 100))
        queue = Att("queue_job", kwargs.get("queue", 1))
        channel = Att("waves", kwargs.get("channel", 304))
        notrack = Att("notrack", kwargs.get("notrack", 1))
        start_time = Att("event_starttime", start)
        end_time = Att("event_endtime", end)
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
        temp.extend([Att(key, kwargs[key]) for key in kwargs])
        self.params = build_from_defaults(defaults, temp)

        self.event = None

        self.service_request_id = None
        self.job_id = None  # The SSW job ID

        # We want to avoid making unnecessary requests.
        # If allow similar is false (default) then Cutout_Request first checks database for any fits files with this event as an id.
        # If it finds such an event, it sets this request's job_id to the job id of the first item it finds (if there are many).
        # This causes the request step to skip (since a request has already been made, and we now have the job id of that request)

        self.fovx = abs(self.event.x_max - self.event.x_min)
        self.fovy = abs(self.event.y_max - self.event.y_min)
        self.notrack = 1

        self.reponse = None  # The requests response
        self._data = None  # The text from the response

        # The is the template for the URL where the job will be located when it completes

    @property
    def data(self):
        return self._data

    def __parse_attributes(self, params, **kwargs):
        other = [Att(key, kwargs[key]) for key in kwargs]
        new_params = build_from_defaults(params, other)
        return {att.name: att.value for att in new_params}

    def submit_request(self) -> None:
        """
        Make a request to the SSW server in order to begin processing.

        :return: None
        :rtype: None
        """
        if not self.job_id:
            try:
                self.response = requests.get(
                    Cutout_Service.base_api_url, params=__parse_attributes(self.params)
                )
            except HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")  # Python 3.6
            except Exception as err:
                print(f"Other error occurred: {err}")  # Python 3.6
            else:
                # print(f"Successfully submitted request ")
                self.job_id = re.search('<param name="JobID">(.*)</param>', self.data)[
                    1
                ]

    def fetch_data(self, delay=None) -> None:
        """
        Attempt to fetch the data from the ssw_server.
        :return: None
        :rtype: None
        """
        data_response_url = Cutout_Request.data_response_url_template.format(
            ssw_id=self.job_id
        )
        data_acquired = False  # Have we been able to get the data_file list?

        delay_time = delay if delay else Cutout_Service.delay_time

        while not data_acquired:

            # In the below statements, we fetch the html from the data_response_url
            # We then check if the response contains the string "Per-Wave file lists", to determine
            # if the request has been processed
            try:
                self.data_response = requests.get(self.data_response_url)
            except HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")  # Python 3.6
            except Exception as err:
                print(f"Other error occurred: {err}")  # Python 3.6
            else:
                if re.search("Per-Wave file lists", self.data_response.text):
                    data_acquired = True
                else:
                    # print("Data not available")
                    time.sleep(delay_time)
                    # print(f"Attempting to fetch data from {self.data_response_url}")
        # print("Data now available")
        # Once the response has been processed we need to extract the list of fits files
        if data_acquired:
            self.status = "completed"
            fits_list_url = re.search(
                '<p><a href="(.*)">.*</a>', self.data_response.text
            )[1]

            if not fits_list_url:
                # print(f"Looks like there are no cut out files available")
                return False

            # List_files_raw contains the pure text from the page listing the urls
            # We then split and extract the actial name
            list_files_raw = requests.get(self.data_response_url + fits_list_url).text
            file_list = list_files_raw.split("\n")
            file_list = [re.search(".*/(.*)$", x)[1] for x in self.file_list if x]
            self._data = self._as_fits(file_list)

    def save_data(self):
        pass

    def save_request(self):
        if self.service_request_id:
            req = Service_Request.get_by_id(self.service_request_id)
        else:
            req = Service_Request()

        if self.event:
            req.event = self.event
        else:
            req.event = None

        req.service_type = "cutout"
        req.status = self.status

        req.job_id = self.job_id

        params_list = []
        existing_param_list = [p for p in req.parameters]

        for param in self.params:
            search = [x for x in existing_param_list if x.key == param.key]
            if search:
                param_list.append(param)
            else:
                param_list.append(search[0])

        req.save()
        for p in param_list:
            p.save()

    def complete_execution(self) -> None:
        """
        A helper method to execute the request and fetch data in one step
    
        :return: None
        :rtype: None
        """

        self.request()
        self.save_request()
        self.fetch_data()

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
        if self.event:
            sol = self.event.sol_standard
        else:
            sol = "unknown"

        data_response_url = Cutout_Request.data_response_url_template.format(
            ssw_id=self.job_id
        )

        for fits_server_file in self.file_list:

            f = Fits_File(
                event=self.event,
                sol_standard=sol,
                ssw_cutout_id=self.job_id,
                server_file_name=fits_server_file,
                server_full_path=data_response_url + fits_server_file,
                file_name=fits_server_file,
            )
            f.file_path = Path(Config["file_save_path"]) / dbs.format_string(
                Config["fits_file_name_format"], f
            )
            ret.append(f)
        return ret


def make_cutout_request(c: Cutout_Request) -> Cutout_Request:
    """
    A wrapper function for processing cutout requests

    :param c: The request
    :type c: Cutout_Request
    :return: The request after executing both the request and fetch stages
    :rtype: Cutout_Request
    """
    c.complete_execution()
    c.as_fits()
    return c


def multi_cutout(list_of_reqs: List[Cutout_Request]) -> List[Cutout_Request]:
    """
    A multithreaded cutout requester. 
    Accepts a list of cutout requests, processes them in paralle and then returns a list of the 
    processed requests

    WARNING: The order of the original list is not guaranteed to be preserved in the returned list

    :param list_of_reqs: List of requests to be processed
    :type list_of_reqs: List[Cutout_Request]
    :return: List of completed request
    :rtype: List[Cutout_Request]
    """
    with ThreadPoolExecutor(max_workers=1000) as executor:
        total_jobs = len(list_of_reqs)
        completed = 0
        print("Starting Requests")
        print(
            f"Currently there are {completed} finished fetches and {total_jobs-completed} pending fetches",
            end="\r",
        )
        cmap = {executor.submit(make_cutout_request, c): c for c in list_of_reqs}
        ret = []

        for future in concurrent.futures.as_completed(cmap):
            ret.append(future.result())
            completed += 1
            print(
                f"Currently there are {completed} finished fetches and {total_jobs-completed} pending fetches",
                end="\r",
            )
        print("\nDone")
    return ret


if __name__ == "__main__":
    c = Cutout_Service()
