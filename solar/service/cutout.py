from __future__ import annotations
from typing import List, Dict
import requests
from datetime import datetime, timedelta
from requests.exceptions import HTTPError
import re
import time
from solar.common.config import Config
from solar.database.tables.hek_event import Hek_Event
from solar.database.tables.fits_file import Fits_File
from solar.database.tables.service_request import Service_Request
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from .attribute import Attribute as Att
from .utils import build_from_defaults
from .request import Base_Service
import peewee as pw
from solar.common import chat
import math


class Cutout_Service(Base_Service):

    # The base url for the ssw response, a response from this returns, most importantly, the job ID associated with this cutout request
    base_api_url = "http://www.lmsal.com/cgi-ssw/ssw_service_track_fov.sh"

    data_response_url_template = "https://www.lmsal.com/solarsoft//archive/sdo/media/ssw/ssw_client/data/{ssw_id}/"
    delay_time = 60  # seconds
    service_type = "cutout"

    @staticmethod
    def _from_event(event: Hek_Event, strict: bool = True) -> Cutout_Service:
        """
        Create a cutout service object from a solar event.

        :param event: The event used to generate the parameters for the request
        :type event: Hek_Event
        :param strict: Whether to allow the program to make decisions that reduce the possibility of duplicate requests, defaults to True
        :type strict: bool, optional
        :return: The constructed cutout service object
        :rtype: Cutout_Service
        """

        # TODO: Add feature that detects if there is an existing request in a similar region as this event #
        if strict:
            try:
                # Can we find an an existing service request that used this event?
                c = Service_Request.get(
                    Service_Request.event == event,
                    Service_Request.service_type == "cutout",
                )
                chat(f"I found a cutout request for event {event.__repr__()}")
                return Cutout_Service._from_model(c)
            except pw.DoesNotExist:
                pass
        chat("I could not find request matching this event, I will create a new one")
        # Either way, we get the parameters we need from the event
        hek_xr = abs(event.x_max - event.x_min)
        hek_yr = abs(event.y_max - event.y_min)
        min_xyr = 120. # in arcsec 
        to_pass = dict(
            xcen=event.hpc_x,
            ycen=event.hpc_y,
            fovx=max(min_xyr,hek_xr),
            fovy=max(min_xyr,hek_yr),
            notrack=1,
            starttime=event.start_time,
            endtime=event.end_time,
        )
        c = Cutout_Service(**to_pass)
        c.event = event
        return c

    @staticmethod
    def _from_model(mod):
        """
        Load a Cutout_Service object from an existing request


        :param mod: The Service_Request object
        :type mod: Service_Request
        :return: A request with parameters built from mod
        :rtype: Cutout_Service
        """
        params = [Att.from_model(x) for x in mod.parameters]
        cut = Cutout_Service(*params)
        cut.event = mod.event
        cut.status = mod.status
        cut.service_request_id = mod.id
        cut.job_id = mod.job_id

        return cut

    def __init__(self, *args, **kwargs):
        """
        Initialize a cutout request.

        - Args may be attributes of the form: Attribute(name,value)
        - Kwargs may be attributes in the form : name=value

        These two will produce equivalent searches

        A list of all attributes may be found at `SSW API <https://www.lmsal.com/solarsoft//ssw_service/ssw_service_track_fov_api.html>`_.
        """
        self.service_request_id = None
        self.job_id = None  # The SSW job ID

        start = datetime.strptime("2010-06-01T00:00:00", Config.time_format.hek)
        end = datetime.strptime("2010-07-01T00:00:00", Config.time_format.hek)

        # A collection of default arguments to make sure that even if the user
        # does not include enough data, a reasonable request can be made
        xcen = Att("xcen", kwargs.get("xcen", 0))
        ycen = Att("ycen", kwargs.get("ycen", 0))
        fovx = Att("fovx", kwargs.get("fovx", 100))
        fovy = Att("fovy", kwargs.get("fovy", 100))
        queue = Att("queue_job", kwargs.get("queue", 1))
        channel = Att("waves", kwargs.get("channel", 304))
        notrack = Att("notrack", kwargs.get("notrack", 1))
        start_time = Att("starttime", start, t_format=Config.time_format.hek)
        end_time = Att("endtime", end, t_format=Config.time_format.hek)

        # A temporary list to hold the arguments submitted by the user
        temp = []
        temp.extend(args)
        temp.extend(
            [Att(key, kwargs[key], t_format=Config.time_format.hek) for key in kwargs]
        )

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

        # Replace default arguments with user submitted ones when possible
        self.params = build_from_defaults(defaults, temp)

        temp_start, = [x for x in self.params if x.name == "starttime"]
        temp_end, = [x for x in self.params if x.name == "endtime"]
        self.params.append(self.__compute_frames(temp_start, temp_end))

        self.event = None

        self.status = "unsubmitted"

        self._data = None  # The text from the response

    def __compute_frames(self, start_time, end_time, cadence=24):
        seconds = math.ceil(
            (end_time.value - start_time.value) / timedelta(seconds=cadence)
        )
        return Att("max_frames", seconds)

    @property
    def data(self):
        """
        A list of :class:`~solar.database.tables.fits.Fits_File` retrieved from the request.
        """
        return self._data

    @data.setter
    def data(self, val):
        self._data = val

    def __parse_attributes(self, **kwargs):
        """
        Convert an attribute list into a dict.

        :param kwargs: Additional parameters to pass append to the created dict. If espy. Note that these parameters are of a higher precedence than the parameters stored in this request
        """
        other = [
            Att(key, kwargs[key], t_format=Config.time_format.hek) for key in kwargs
        ]
        new_params = build_from_defaults(self.params, other)
        return {att.name: att.f_value() for att in new_params}

    def submit_request(self, auto_save=True):
        """
        Make a request to the SSW server in order to begin processing. 

        :param auto_save: whether to autosave the request, defaults to True
        :type auto_save: bool
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
                # Extract the job_id from the response
                self.job_id = re.search(
                    '<param name="JobID">(.*)</param>', response.text
                )[1]

        self.status = "submitted"
        if auto_save:
            self.save_request()

    def fetch_data(self, delay=None, auto_save=True):
        """Function fetch_data: 
        Attempt to fetch the data from the ssw_server.

        :param delay: The time to wait between requests, defaults to None
        :type delay: int
        :param auto_save: Save the request automatically, defaults to True
        :type auto_save: bool
        """

        if not self.job_id:
            self.submit_request(auto_save=auto_save)

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
                self._data = [self._as_fits(x) for x in file_list]

    def save_data(self):
        """Save the fits files generated by the request to the database
        """
        for i in range(len(self._data)):
            try:
                self._data[i].save()
            except pw.IntegrityError as e:
                self._data[i] = Fits_File.get(
                    Fits_File.server_full_path == self._data[i].server_full_path
                )
            except Exception as e:
                print(e)

    def _as_fits(self, fits_server_file) -> Fits_File:
        """
        Use the fits file list to construct and insert fits_files into the database.
        Note that this does not download the files. That is done through the
        update_table command.

        :param file_list: A list of server_file_names
        :type file_list: List[str]
        :return: List of fits files (already inserted;w
        :rtype: List[Fits_File]
        """
        sol = self.event.sol_standard if self.event else "unknown"
        event_id = self.event.event_id if self.event else None
        req_id = self.service_request_id if self.service_request_id else None

        data_response_url = Cutout_Service.data_response_url_template.format(
            ssw_id=self.job_id
        )

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
        return f


def c_fetch(c: Cutout_Service, auto_save=True) -> Cutout_Service:
    """
    A wrapper function for processing cutout requests

    :param c: The request
    :type c: Cutout_Service
    :return: The request after executing both the request and fetch stages
    :retype: Cutout_Service
    """
    c.fetch_data()
    if auto_save:
        c.save_request()
    return c


def multi_cutout(list_of_reqs: List[Cutout_Service]) -> List[Cutout_Service]:
    """
    A multi threaded cutout requester. 
    Accepts a list of cutout requests, processes them in parallel and then returns a list of the 
    processed requests

    WARNING: The order of the original list is not guaranteed to be preserved in the returned list

    :pram list_of_reds: List of requests to be processed
    :type list_of_reds: List[Cutout_Service]
    :return: List of completed request
    :retype: List[Cutout_Service]
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
