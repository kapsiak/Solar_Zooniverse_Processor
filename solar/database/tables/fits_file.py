import peewee as pw
import json
from solar.common.config import Config
from datetime import datetime
from solar.service.downloads import multi_downloader, download_single_file
from pathlib import Path
from sunpy.map import Map
from .base_models import File_Model
from .ucol import UnionCol, List_Storage
from .hek_event import Hek_Event
from tqdm import tqdm
from typing import Any, Dict
from .service_request import Service_Request
import shutil
from solar.database.utils import dbformat, dbroot
from solar.common.utils import into_number


class Fits_File(File_Model):
    file_name_format = Config.file_storage.fits
    file_path_format = Config.storage_path.fits
    """
    The database table that stores fits files, mostly downloaded from the ssw cutout service

    """

    #: Foreign key to the :class:`~solar.database.tables.hek_event.Hek_Event` from which this fits_file was found, if any.
    event = pw.ForeignKeyField(Hek_Event, backref="fits_files", null=True)

    #: Foreign key to the :class:`~solar.database.tables.service_request.Service_Request` from which this fits_file was found, if any.
    request = pw.ForeignKeyField(Service_Request, backref="fits_files", null=True)

    #: The sol standard of the event
    sol_standard = pw.CharField(null=True)

    #: The name of the file on the SSW server
    server_file_name = pw.CharField(null=True)
    #: The full path to the file on the ssw server
    server_full_path = pw.CharField(unique=True, null=True)
    
    #: The job id from which this fits file was generated
    ssw_cutout_id = pw.CharField(null=True)

    #: The image time in the fits header
    image_time = pw.DateTimeField(default=None, null=True)

    def __repr__(self) -> str:
        return f"<fits_instance:{self.sol_standard}|{self.file_path}>"

    def __str__(self):
        return f"""
ID              = {self.id}
Event (ID/SOL)  = {self.event.sol_standard} | {self.sol_standard}
Server_Path     = {self. server_full_path}
File_Path       = {self.file_path}
Hash            = {self.file_hash}
            """

    @staticmethod
    def make_path(fits_model, default_format=Config.storage_path.fits, **kwargs):
        return dbroot(dbformat(default_format, fits_model, **kwargs))

#    @staticmethod
#    def from_file(file_path, file_name):
#        new_path = Config["fits_unkown_name_format"].format(file_name=file_name)
#        try:
#            fits = Fits_File.create(full_path=new_path, file_name=file_name)
#        except pw.IntegrityError:
#            print("Already in database")
#            return Fits_File.get(Fits_File.full_path == new_path)
#        except Exception as e:
#            print(e)
#            return None
#        else:
#            shutil.copy(file_path, new_path)
#            fits.get_hash()
#            return fits

    def update_single(self):
        """Function update_single: 

        If integrity check fails, attempt to fetch and update a single fits file.
        """
        if not self.check_integrity():
            if self.server_full_path:
                download_single_file(self.server_full_path, self.file_path)
                self.get_hash()
                self.extract_fits_data()
                self.image_time = datetime.strptime(
                    self["date-obs"], Config.time_format.fits
                )
                self.save()

    @staticmethod
    def update_table(update_headers: bool = True):
        """
        Update the database. Attempts to download any missing fits files and extracts the headers from all :class:`Fits_File`s in the database.

        :param update_headers: whether to update headers, defaults to True
        :type update_headers: bool, optional
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
                f.image_time = datetime.strptime(f["date-obs"], Config.time_format.fits)
                f.save()

        print(f"Update complete")

    def extract_fits_data(self):
        """
        Extract data from the associated fits file, and save it in the Fits_Header_Elem table
        """
        if Path(self.file_path).is_file():
            m = Map(self.file_path)
            header = m.meta
            header = {x: y for x, y in m.meta.items() if not isinstance(y, dict)}
            for h_key in header:
                f = self.fits_keys.where(Fits_Header_Elem.key == h_key)
                if not f.exists():
                    f = Fits_Header_Elem(fits_file=self, key=h_key)
                    f.format = Config.time_format.fits
                    f.value = header[h_key]
                    f.save()
                else:
                    f = f.get()
                    f.key = h_key
                    f.format = Config.time_format.fits
                    f.value = header[h_key]
                    f.save()

    def __getitem__(self, key: str) -> Any:
        """
        Get an item. References the Fits_Header_Elem table to get the value of a header key

        :param key: The header key
        :type key: str
        :return: The value associated with the key
        :rtype: Any
        """
        return self.fits_keys.where(Fits_Header_Elem.key == key).get().value

    def get_header_as_dict(self):
        """
    
        Get the fits header as a dictionary, using the existing fits header elems stored in the database.
        Warning! If fits_header_elem has been modified, then the fits header returned by the function may not match the one in the fits file.

        :returns: Fits header formatted as a dict
        :type return: dict
        """
        return {x.key: x.value for x in self.fits_keys}

    def get_header_as_json(self):
        """
        Get the fits header as json, using the existing fits header elems stored in the database.
        Warning! If fits_header_elem has been modified, then the fits header returned by the function may not match the one in the fits file.

        :returns: Fits header formatted as a json
        :type return: json
        """
        return json.dumps(self.get_header_as_dict())

    def __iter__(self):
        return (x for x in self.fits_keys)


class Fits_Header_Elem(UnionCol):
    fits_file = pw.ForeignKeyField(Fits_File, backref="fits_keys")
    key = pw.CharField(default="NA")

    def __repr__(self) -> str:
        return f"<Header {self.key}:{self.value}>"

    def __str__(self) -> str:
        return f"{self.key}: {self.value}"


class Fits_Header_Elem_List(List_Storage):
    table = pw.ForeignKeyField(Fits_Header_Elem, backref="list_values")


# We must add this after the class has been declared to avoid circular issues
Fits_Header_Elem.list_storage_table = Fits_Header_Elem_List
