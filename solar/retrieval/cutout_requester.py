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
from solar.database import Solar_Event, Fits_File
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import tqdm
from peewee import DoesNotExist


class Cutout_Request:

    # The base url for the ssw response, a response from this returns, most importatnyl, the job ID associated with this cuttout request
    base_url = "http://www.lmsal.com/cgi-ssw/ssw_service_track_fov.sh"
    data_response_url_template = "https://www.lmsal.com/solarsoft//archive/sdo/media/ssw/ssw_client/data/{ssw_id}/"

    def __init__(
        self, event: Union[Solar_Event, str], allow_similar: bool = False
    ) -> None:
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

        if isinstance(event, str):
            self.event = Solar_Event.select().where(Solar_Event.event_id == event).get()
            # If user attempts to use an event that does not exist in the database, raise DoesNotExist
        else:
            self.event = event

        # Information associated with the event. The event id is the SOL, and be default the fits data will be saved to ./fits/EVENT_ID/
        self.job_id = None  # The SSW job ID

        # We want to avoid making unnecessary requests.
        # If allow similar is false (default) then Cutout_Request first checks database for any fits files with this event as an id.
        # If it finds such an event, it sets this request's job_id to the job id of the first item it finds (if there are many).
        # This causes the request step to skip (since a request has already been made, and we now have the job id of that request)
        if not allow_similar:
            try:
                existing_file = self.event.fits_files.get()
            except DoesNotExist:
                pass
            else:
                self.job_id = existing_file.ssw_cutout_id
                print(
                    f"I found a similar query, and I am going to use the job id {self.job_id}"
                )
                print(
                    f"If you do not want this behavior, please set allow_similar=True"
                )

        # Information associated with the cuttout request
        self.fovx = abs(self.event.x_max - self.event.x_min)
        self.fovy = abs(self.event.y_max - self.event.y_min)
        self.notrack = 1

        self.reponse = None  # The requests response
        self.data = None  # The text from the response

        # The is the template for the URL where the job will be located when it completes

        # The data_response url after the job id has been subsitituted in
        self.data_response_url = None
        # The requests object associated with the response
        self.data_response = None
        # How long in seconds to wait between making requests (to avoid overwhelming the server)
        self.delay_time = 60

        # A list of the fits files
        self.file_list = []

    def request(self) -> None:
        """
        Make a request to the SSW server in order to begin processing.

        :return: None
        :rtype: None
        """
        if not self.job_id:
            try:
                self.response = requests.get(
                    self.base_url,
                    params={
                        "starttime": self.event.start_time.strftime(
                            Config["time_format_hek"]
                        ),
                        "endtime": self.event.end_time.strftime(
                            Config["time_format_hek"]
                        ),
                        "instrume": "aia",
                        "xcen": self.event.hgc_x,
                        "ycen": self.event.hgc_y,
                        "fovx": self.fovx,
                        "fovy": self.fovy,
                        "max_frames": 10,
                        "waves": 304,
                        "queue_job": 1,
                    },
                )
            except HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")  # Python 3.6
            except Exception as err:
                print(f"Other error occurred: {err}")  # Python 3.6
            else:
                #print(f"Successfully submitted request ")
                self.data = self.response.text
                self.job_id = re.search('<param name="JobID">(.*)</param>', self.data)[
                    1
                ]

        self.data_response_url = Cutout_Request.data_response_url_template.format(
            ssw_id=self.job_id
        )

    def fetch_data_file_list(self) -> None:
        """
        Attempt to fetch the data from the ssw_server.
        :return: None
        :rtype: None
        """
        if not self.data_response_url:
            self.data_response_url = Cutout_Request.data_response_url_template.format(
                ssw_id=self.job_id
            )
        data_acquired = False  # Have we been able to get the data_file list?
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
                    #print("Data not available")
                    time.sleep(self.delay_time)
                    #print(f"Attempting to fetch data from {self.data_response_url}")
        #print("Data now available")
        # Once the response has been processed we need to extract the list of fits files
        if data_acquired:
            fits_list_url = re.search(
                '<p><a href="(.*)">.*</a>', self.data_response.text
            )[1]
            if not fits_list_url:
                #print(f"Looks like there are no cut out files available")
                return False

            # List_files_raw contains the pure text from the page listing the urls
            # We then split and extract the actial name
            list_files_raw = requests.get(self.data_response_url + fits_list_url).text
            self.file_list = list_files_raw.split("\n")
            self.file_list = [re.search(".*/(.*)$", x)[1] for x in self.file_list if x]

    def complete_execution(self) -> None:
        """
        A helper method to execute the request and fetch data in one step
    
        :return: None
        :rtype: None
        """

        self.request()
        self.fetch_data_file_list()

    def as_fits(self) -> List[Fits_File]:
        """
        Use the fits file list to construct and insert fits_files into the database.
        Note that this does not download the files. That is done through the
        update_table command.

        :return: List of fits files (already inserted;w
        :rtype: List[Fits_File]
        """
        ret = []
        for fits_server_file in self.file_list:
            try:
                f = Fits_File.get(
                    event=self.event,
                    sol_standard=self.event.sol_standard,
                    ssw_cutout_id=self.job_id,
                    server_file_name=fits_server_file,
                    server_full_path=self.data_response_url + fits_server_file,
                    file_name=fits_server_file,
                )

            except DoesNotExist:
                f = Fits_File.create(
                    event=self.event,
                    sol_standard=self.event.sol_standard,
                    ssw_cutout_id=self.job_id,
                    server_file_name=fits_server_file,
                    server_full_path=self.data_response_url + fits_server_file,
                    file_name=fits_server_file,
                )

            f.file_path = Path(Config["file_save_path"]) / dbs.format_string(
                Config["fits_file_name_format"], f, file_type="FITS"
            )
            f.save()
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
    :return: List of completed request:238
    :rtype: List[Cutout_Request]
    """
    with ThreadPoolExecutor(max_workers=1000) as executor:
        total_jobs = len(list_of_reqs)
        completed = 0 
        print("Starting Requests")
        print(f"Currently there are {completed} finished fetches and {total_jobs-completed} pending fetches", end = '\r')
        cmap = {executor.submit(make_cutout_request, c): c for c in list_of_reqs}
        ret = []

        for future in concurrent.futures.as_completed(cmap):
            ret.append(future.result())
            completed += 1
            print(f"Currently there are {completed} finished fetches and {total_jobs-completed} pending fetches", end='\r')
        print("\nDone")
    return ret
