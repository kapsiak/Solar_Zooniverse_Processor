import requests
from datetime import datetime
from requests.exceptions import HTTPError
import re
from pathlib import Path
import time
import sys
import threading
import concurrent.futures
from solar.common.solar_event import Solar_Event
import solar.solar_database.database as db


def get_ssw_from_database(connection,event_id):
    data = connection.execute("SELECT (ssw_job_id) FROM hek_events WHERE event_id=? AND NOT ssw_job_id='NO_REQUEST'",(event_id,))
    ret = data.fetchone()
    if ret:
        return ret[0]
    else:
        return False


def download_file(from_url, target):
    with open(target, "wb") as f:
        f.write(requests.get(from_url).content)


class Cutout_Request:
    def __init__(
        self,
        event,
        repeat_query=True,
        verbose = True
    ):
        self.e = event

        # Information associated with the event. The event id is the SOL, and be default the fits data will be saved to ./fits/EVENT_ID/
        self.download_dir = Path("fits")
        self.save_dir = self.e.event_id
        self.save_dir = self.download_dir / self.save_dir

        # Information associated with the cuttout request
        self.xcen = (self.e.x_min + self.e.x_max) / 2
        self.ycen = (self.e.y_min + self.e.y_max) / 2
        self.fovx = abs(self.e.x_max - self.e.x_min)
        self.fovy= abs(self.e.y_max - self.e.y_min)
        self.notrack = 1
        self.waves = 304
        

        # The base url for the ssw response, a response from this returns, most importatnyl, the job ID associated with this cuttout request
        self.base_url = "http://www.lmsal.com/cgi-ssw/ssw_service_track_fov.sh"
        # The requests response
        self.reponse = None
        # The text from the response
        self.data = None
        # The SSW job ID
        self.job_id = None

        # The is the template for the URL where the job will be located when it completes
        self.data_response_url_template = "https://www.lmsal.com/solarsoft//archive/sdo/media/ssw/ssw_client/data/{ssw_id}/"

        # The data_response url after the job id has been subsitituted in
        self.data_response_url = None
        # The requests object associated with the response
        self.data_response = None
        # How long in seconds to wait between making requests (to avoid overwhelming the server)
        self.delay_time = 60

        # The text from the site where the files are lists
        self.files_list_raw = None
        # A list of the fits files
        self.file_list = []


        #currently unused
        self.verbose = verbose

        self.connection = db.get_connection()


        self.ssw_in_database = False



    def add_to_database(self,connection):
        if self.job_id:
            db.update_record(connection, self.e, 'ssw_job_id' , self.job_id)

    def request(self):
        """
        Make a request to the SSW server in order to begin processing
        returns: 
            self.data -> text from the response
            self.job_id -> The job id of the ssw_process
         
        """
        
        self.job_id = get_ssw_from_database(db.get_connection(),self.e.event_id)
        print(self.job_id)
        if self.job_id:
            temp_url = self.data_response_url_template.format(
            ssw_id=self.job_id
        )

            print(f"""Looks like the event with id {self.e.event_id} is already in process 
                    The ID is: {self.job_id}
                    The status may be views at {temp_url}
                    """)
        else:
            try:
                self.response = requests.get(
                    self.base_url,
                    params={
                        "starttime": self.e.start_time,
                        "endtime": self.e.end_time,
                        "instrume": self.e.instrument,
                        "notrack": self.notrack,
                        "xcen": self.xcen,
                        "ycen": self.ycen,
                        "fovx": self.fovx,
                        "fovy": self.fovy,
                        "max_frames": 10,
                        "waves": self.waves,
                        "queue_job": 1,
                    },
                )
            except HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")  # Python 3.6
            except Exception as err:
                print(f"Other error occurred: {err}")  # Python 3.6
            else:
                print(
                    f"Successfully submitted request "
                    f"from times {self.e.start_time}"
                    f" to {self.e.end_time} "
                )
                self.data = self.response.text
                self.job_id = re.search('<param name="JobID">(.*)</param>', self.data)[1]
                self.add_to_database(db.get_connection())
        self.data_response_url = self.data_response_url_template.format(
            ssw_id=self.job_id
        )

    def fetch_data(self):
        if self.job_id == None:
            self.request()

        data_acquired = False
        while not data_acquired:
            self.data_response = requests.get(self.data_response_url)
            if re.search("Per-Wave file lists", self.data_response.text):
                data_acquired = True
            else:
                print("Data not available") 
            time.sleep(self.delay_time)
            print(f"Attempting to fetch data from {self.data_response_url}") 
        print("Data now available") 
        if data_acquired:
            fits_list_url = re.search(
                '<p><a href="(.*)">.*</a>', self.data_response.text
            )[1]
            if not fits_list_url:
                print(f"Looks like there are no cut out files available")
                return False
            list_files_raw = requests.get(self.data_response_url + fits_list_url).text
            self.file_list = list_files_raw.split("\n")
            self.file_list = [re.search(".*/(.*)$", x)[1] for x in self.file_list if x]

    def download_fits_files(self, save_dir_loc=None):
        save_dir = save_dir_loc if save_dir_loc else self.save_dir
        self.save_dir.mkdir(parents=True, exist_ok=True)
        download_list = [file_path for file_path in self.file_list if not (save_dir / fits_file_url).exists()]
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for fits_file_url in download_list:
                executor.submit(download_file, self.data_response_url + fits_file_url , save_dir / fits_file_url)

    def execute_full(self,connection):
        self.job_id = self.get_ssw_from_database(connection)
        if not self.job_id:
            self.request()
        self.fetch_data()
        self.download_fits_files()



def cuttout_wrapper(event):
    c = Cutout_Request(c)
    c.execute_full()


def multithread_cuttout(list_of_events):
    with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
        for event in list_of_events:
            executor.submit(cuttout_wrapper,event)



