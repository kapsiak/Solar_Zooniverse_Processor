import peewee as pw
from solar.database import database as db
from solar.common.config import Config
import solar.database.string as dbs
from datetime import datetime
from solar.retrieval.downloads import multi_downloader
from pathlib import Path
from solar.common.utils import checksum, into_number
from sunpy.map import Map
import astropy.units as u
from sunpy.io.header import FileHeader
import numpy as np


def prepend_root(path):
    return str(Path(Config["file_save_path"]) / path)


class BaseModel(pw.Model):
    @classmethod
    def update_table(cls):
        pass

    class Meta:
        database = db


class File_Model(BaseModel):

    file_path = pw.CharField(default="NA")
    file_hash = pw.CharField(default="NA")
    file_name = pw.CharField(defailt="NA")

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

    frm_identifier = pw.CharField(default="NA")

    search_frm_name = pw.CharField(default="NA")

    description = pw.CharField(default="NA")

    @staticmethod
    def from_hek(h, source):
        return Solar_Event(
            event_id=h["SOL_standard"],
            sol_standard=h["SOL_standard"],
            start_time=datetime.strptime(
                h["event_starttime"], Config["time_format_hek"]
            ),
            end_time=datetime.strptime(h["event_endtime"], Config["time_format_hek"]),
            coord_unit=h["event_coordunit"],
            x_min=h["boundbox_c1ll"],
            x_max=h["boundbox_c1ur"],
            y_min=h["boundbox_c2ll"],
            y_max=h["boundbox_c2ur"],
            hgc_x=h["hgc_x"],
            hgc_y=h["hgc_y"],
            hpc_x=h["hpc_x"],
            hpc_y=h["hpc_y"],
            frm_identifier=h["frm_identifier"],
            search_frm_name=h["search_frm_name"],
            description=h["event_description"],
            source=source,
        )

    def __repr__(self):
        return f""" {self.event_id}: {self.description}"""


class Fits_File(File_Model):

    event = pw.ForeignKeyField(Solar_Event, backref="fits_files")

    sol_standard = pw.CharField(default="NA")

    server_file_name = pw.CharField(default="NA")
    server_full_path = pw.CharField(default="NA")

    ssw_cutout_id = pw.CharField(default="NA")

    image_time = pw.DateTimeField(default=datetime.now())

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
        self.file_path = prepend_root(
            dbs.format_string(Config[f"fits_file_name_format"], self, file_type="FITS")
        )
        self.file_path = self.file_path.replace(":", "-")
        self.save()

    @staticmethod
    def update_table():
        Fits_File.correct_path_database()
        bad_files = [x for x in Fits_File.select() if not x.check_integrity()]
        needed = None
        with db:
            needed = {f.server_full_path: f.file_path for f in bad_files}
        print(f"Found {len(bad_files)} missing/corrupted files")
        multi_downloader(needed)
        for f in bad_files:
            f.get_hash()

        for f in Fits_File.select():
            f.extract_fits_data()
            f.image_time = datetime.strptime(
                f["date-obs"], Config["time_format_from_fits"]
            )

        print(f"Update complete")

    def extract_fits_data(self):
        if Path(self.file_path).is_file():
            print(f"Extracting data from {self.id}")
            m = Map(self.file_path)
            header = m.meta
            for h_key in header:
                f = self.fits_keys.where(Fits_Header_Elem.key == h_key)
                if not f:
                    f = Fits_Header_Elem.create(
                        fits_file=self, key=h_key, value=header[h_key]
                    )
                else:
                    f = f.get()
                    f.key = h_key
                    f.value = header[h_key]
                    f.save()
            self.save()

    def __getitem__(self, key):
        return into_number(
            self.fits_keys.where(Fits_Header_Elem.key == key).get().value
        )

    def get_header_as_dict(self):
        return {x.key: into_number(x.value) for x in self.fits_keys}


class Image_File(File_Model):

    fits_file = pw.ForeignKeyField(Fits_File, backref="image_file")

    image_type = pw.CharField(default="png")

    description = pw.CharField(default="NA")

    frame = pw.BooleanField(default=False)

    ref_pixel_x = pw.IntegerField(default=0)
    ref_pixel_y = pw.IntegerField(default=0)

    @staticmethod
    def create_new_image(fits_file, image_maker, file_name=None, desc=""):
        if not file_name:
            file_name = fits_file.file_name
            file_name = Path(file_name).stem
        file_path = str(
            Path(
                prepend_root(
                    Config["img_file_name_format"].format(
                        image_type=image_maker.file_type,
                        sol_standard=fits_file.sol_standard,
                        file_name=file_name,
                    )
                )
            ).with_suffix("." + image_maker.image_type)
        )
        image_maker.create()
        image_maker.save(file_path)

        im = Image_File.create(
            fits_file=fits_file,
            image_type=image_maker.image_type,
            description=desc,
            frame=image_maker.frame,
            ref_pixel_x=image_maker.ref_pixel_x,
            ref_pixel_y=image_maker.ref_pixel_y,
        )

        im.get_hash()
        return im

    def correct_file_path(self):
        self.file_path = prepend_root(
            dbs.format_string(Config[f"img_file_name_format"], self, file_type="FITS")
        )
        self.file_path = self.file_path.replace(":", "-")
        self.save()

    def get_world_from_pixels(self, x, y):
        header_dict = FileHeader(self.fits_file.get_header_as_dict())
        fake_map = Map(np.zero((1, 1)), header_dict)
        return fake_map.pixel_to_world(x * u.pix, y * u.pix)


class Fits_Header_Elem(BaseModel):
    fits_file = pw.ForeignKeyField(Fits_File, backref="fits_keys")
    key = pw.CharField(default="NA")
    value = pw.CharField(default="NA")

    def __repr__(self):
        return f"<Header {self.key}:{self.value}>"

    def __str__(self):
        return f"{self.key}: {self.value}"


TABLES = [Solar_Event, Fits_File, Fits_Header_Elem, Image_File]


def create_tables():
    with db:
        db.create_tables(TABLES)
