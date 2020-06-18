import peewee as pw
from solar.database import database as db
from solar.database.utils import prepend_root, format_string
from solar.common.config import Config
from datetime import datetime
from solar.service.downloads import multi_downloader
from pathlib import Path
from solar.common.utils import checksum, into_number
from sunpy.map import Map
import astropy.units as u
from sunpy.io.header import FileHeader
import numpy as np
from .base_models import File_Model, Base_Model
from .solar_event import Solar_Event
from tqdm import tqdm
from typing import Any, Dict
from .service_request import Service_Request
import shutil


class Fits_File(File_Model):
    """
    Fits_File
    =============
    """

    event = pw.ForeignKeyField(Solar_Event, backref="fits_files", null=True)
    request = pw.ForeignKeyField(Service_Request, backref="fits_files", null=True)

    sol_standard = pw.CharField(null=True)

    server_file_name = pw.CharField(null=True)
    server_full_path = pw.CharField(unique=True, null=True)

    ssw_cutout_id = pw.CharField(null=True)

    image_time = pw.DateTimeField(default=None, null=True)

    def __repr__(self) -> str:
        return f"<fits_instance:{self.sol_standard}|{self.file_path}>"

    def __str__(self):
        return f""" 
Event (ID/SOL)  = {self.event.sol_standard} | {self.sol_standard}
Server_Path     = {self. server_full_path}
File_Path       = {self.file_path}
Hash            = {self.file_hash}
            """

    @staticmethod
    def from_file(file_path, file_name):
        new_path = Config["fits_unkown_name_format"].format(file_name=file_name)
        try:
            fits = Fits_File.create(full_path=new_path, file_name=file_name)
        except pw.IntegrityError:
            print("Already in database")
            return Fits_File.get(Fits_File.full_path == new_path)
        except Exception as e:
            print(e)
            return None
        else:
            shutil.copy(file_path, new_path)
            fits.get_hash()
            return fits

    @staticmethod
    def update_table(update_headers: bool = True):
        """
        Update the database. 

        :param update_headers: whether to update headers, defaults to True
        :type update_headers: bool, optional
        :return: None      
        :rtype: None
        """
        bad_files = [x for x in Fits_File.select() if not x.check_integrity()]
        gettable = [x for x in bad_files if x.server_full_path]
        gettable_urls = {f.server_full_path: f.file_path for f in gettable}
        print(f"Found {len(bad_files)} missing/corrupted files")
        print(f"I am able to redownload {len(gettable)} of these")
        print(
            f"The remaining {len(bad_files) - len(gettable)} files cannot be retrieved automatically"
        )
        multi_downloader(gettable_urls)
        for f in bad_files:
            f.get_hash()

        num_rows = Fits_File.select().count()
        if update_headers:
            print(f"Updating headers on {num_rows} files")
            for f in tqdm(bad_files, total=len(bad_files), desc="Extracting Data"):
                f.extract_fits_data()
                f.image_time = datetime.strptime(
                    f["date-obs"], Config["time_format_from_fits"]
                )
                f.save()

        print(f"Update complete")

    def extract_fits_data(self) -> None:
        """
        Extract data from the associated fits file, and save it in the Fits_Header_Elem table

        :return: None
        :rtype: None
        """
        if Path(self.file_path).is_file():
            m = Map(self.file_path)
            header = m.meta
            for h_key in header:
                f = self.fits_keys.where(Fits_Header_Elem.key == h_key)
                if not f.exists():
                    f = Fits_Header_Elem.create(
                        fits_file=self, key=h_key, value=header[h_key]
                    )
                else:
                    f = f.get()
                    f.key = h_key
                    f.value = header[h_key]
                    f.save()
            self.save()

    def __getitem__(self, key: str) -> Any:
        """
        Get an item. References the Fits_Header_Elem table to get the value of a header key

        :param key: The header key
        :type key: str
        :return: The value associated with the key
        :rtype: Any
        """
        return into_number(
            self.fits_keys.where(Fits_Header_Elem.key == key).get().value
        )

    def get_header_as_dict(self) -> Dict[str, Any]:
        return {x.key: into_number(x.value) for x in self.fits_keys}


class Fits_Header_Elem(Base_Model):
    fits_file = pw.ForeignKeyField(Fits_File, backref="fits_keys")
    key = pw.CharField(default="NA")
    value = pw.CharField(default="NA")

    def __repr__(self) -> str:
        return f"<Header {self.key}:{self.value}>"

    def __str__(self) -> str:
        return f"{self.key}: {self.value}"
