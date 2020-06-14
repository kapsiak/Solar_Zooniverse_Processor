import peewee as pw
from solar.database import database
from solar.common.config import Config
import solar.database.string as dbs
from datetime import datetime
from solar.retrieval.downloads import multi_downloader
from pathlib import Path
from solar.common.utils import checksum
from sunpy.map import Map
from solar.common.time_format import TIME_FORMAT_HIGH_PREC


class BaseModel(pw.Model):
    @classmethod
    def new(cls, param_dict, **kwargs):
        return cls(**param_dict, **kwargs)

    class Meta:
        database = database


class File_Model(BaseModel):

    file_path = pw.CharField(default="NA")
    file_hash = pw.CharField(default="NA")


    def correct_file_path(self):
        pass

    @classmethod
    def correct_path_database(cls):
        for f in cls.select():
            f.correct_file_path()

    def get_hash(self):
        try:
            self.file_hash = checksum(self.file_path)
        except IOError as e:
            print(f"Could not get hash: {e}")
            self.file_hash = "NA"
        self.save()
        return self.file_hash

    def check_integrity(self):
        p = Path(self.file_path)
        if p.is_file():
            if checksum(self.file_path) == self.file_hash:
                return True
        return False



class Solar_Event(BaseModel):

    event_id = pw.CharField(default="NA", unique=True)
    sol_standard = pw.CharField(default="NA")

    start_time = pw.DateTimeField(default=datetime.now)
    end_time = pw.DateTimeField(default=datetime.now)

    coord_unit = pw.CharField(default="NA")

    x_min = pw.FloatField(default=-1)
    y_min = pw.FloatField(default=-1)

    x_max = pw.FloatField(default=-1)
    y_max = pw.FloatField(default=-1)

    hpc_x = pw.FloatField(default=-1)
    hpc_y = pw.FloatField(default=-1)

    hgc_x = pw.FloatField(default=-1)
    hgc_y = pw.FloatField(default=-1)

    source = pw.CharField(default="NA")

    frm_identifier = pw.CharField(default="NA")

    search_frm_name = pw.CharField(default="NA")

    description = pw.CharField(default="NA")

    def __repr__(self):
        return f""" {self.event_id}: {self.description}"""


class Fits_File(File_Model):

    event = pw.ForeignKeyField(Solar_Event, backref="fits_files")

    sol_standard = pw.CharField(default="NA")

    server_file_name = pw.CharField(default="NA")
    server_full_path = pw.CharField(default="NA")

    file_path = pw.CharField(default="NA")
    file_hash = pw.CharField(default="NA")

    instrument = pw.CharField(default="NA")
    channel = pw.CharField(default="NA")

    coord_sys_1 = pw.CharField(default="NA")
    coord_sys_2 = pw.CharField(default="NA")

    ssw_cutout_id = pw.CharField(default="NA")

    image_time = pw.DateTimeField(default=datetime.now())

    unit_1 = pw.CharField(default="arcsec")
    unit_2 = pw.CharField(default="arcsec")

    reference_pixel_1 = pw.FloatField(default=-1)
    reference_pixel_2 = pw.FloatField(default=-1)
    reference_pixel_wcs_1 = pw.FloatField(default=-1)
    reference_pixel_wcs_2 = pw.FloatField(default=-1)

    pixel_size_1 = pw.FloatField(default=-1)
    pixel_size_2 = pw.FloatField(default=-1)

    im_dim_1 = pw.IntegerField(default=-1)
    im_dim_2 = pw.IntegerField(default=-1)

    def __repr__(self):
        return f"""<fits_instance:{self.sol_standard}|{self.file_path}"""

    def __str__(self):
        return f""" 
Event (ID/SOL)  = {self.event} | {self.sol_standard}
Server_Path     = {self. server_full_path}
File_Path       = {self.file_path}
Hash            = {self.file_hash}
            """

    def correct_file_path(self):
            self.file_path = dbs.format_string(
                Config[f"fits_file_name_format"], self, file_type="FITS"
            )
            self.file_path = self.file_path.replace(":", "-")
            self.save()

    
    @staticmethod
    def update_database():
        bad_files = [x for x in Fits_File.select() if not x.check_integrity()]
        needed = None
        with database:
            needed = {f.server_full_path: f.file_path for f in bad_files}
        print(f"Found {len(bad_files)} missing/corrupted files")
        multi_downloader(needed)
        for f in bad_files:
            f.get_hash()

        for f in Fits_File.select():
            f.extract_fits_data()

        print(f"Update complete")

    def extract_fits_data(self):
        if Path(self.file_path).isfile():
            m = Map(self.file_path)
            header = m.meta

            self.instrument = header["instrume"]
            self.channel = header["wavelnth"]

            self.image_time = datetime.strptime(
                header.date - obs, TIME_FORMAT_HIGH_PREC
            )

            self.unit_1 = header["cunit1"]
            self.unit_2 = header["cunit2"]

            self.reference_pixel_1 = header["crpix1"]
            self.reference_pixel_2 = header["crpix2"]
            self.reference_pixel_wcs_1 = header["crval1"]
            self.reference_pixel_wcs_2 = header["crval2"]

            self.pixel_size_1 = header["cdel1"]
            self.pixel_size_2 = header["cdel2"]

            self.im_dim_1 = header["naxis1"]
            self.im_dim_2 = header["naxis2"]

            self.coord_sys_1 = header["ctype1"]
            self.coord_sys_2 = header["ctype2"]

            self.save()


class Image_File(File_Model):

    fits_file = pw.ForeignKeyField(Fits_File, backref="image_file")

    image_type = pw.CharField(default='png')

    file_path = pw.CharField(default="NA")
    file_hash = pw.CharField(default="NA")

    description = pw.CharField(default="NA")

    frame = pw.BooleanField(default=False)
     
    def correct_file_path(self):
            self.file_path = dbs.format_string(
                Config[f"img_file_name_format"], self, file_type="FITS"
            )
            self.file_path = self.file_path.replace(":", "-")
            self.save()
     


TABLES = [Solar_Event, Fits_File]
