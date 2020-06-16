import peewee as pw
from solar.common.config import Config
from solar.database.utils import prepend_root, format_string
from pathlib import Path
from sunpy.map import Map
import astropy.units as u
from sunpy.io.header import FileHeader
import numpy as np
from .base_models import File_Model, Base_Model
from .fits_file import Fits_File


class Image_File(File_Model):

    fits_file = pw.ForeignKeyField(Fits_File, backref="image_file")

    image_type = pw.CharField(default="png")

    description = pw.CharField(default="NA")

    frame = pw.BooleanField(default=False)

    # width  = pw.IntegerField(default=0)
    # height = pw.IntegerField(default=0)

    ref_pixel_x = pw.IntegerField(default=0)
    ref_pixel_y = pw.IntegerField(default=0)

    @staticmethod
    def create_new_image(fits_file, image_maker, file_name=None, desc="", **kwargs):
        if not file_name:
            file_name = fits_file.file_name
            file_name = Path(file_name).stem
        file_name = Path(file_name).with_suffix("." + image_maker.image_type)
        file_path = str(
            Path(
                prepend_root(
                    Config["img_file_name_format"].format(
                        image_type=image_maker.image_type,
                        sol_standard=fits_file.sol_standard,
                        file_name=file_name,
                    )
                )
            )
        )
        if image_maker.create(fits_file.file_path, **kwargs):
            image_maker.save_image(file_path)

            im = Image_File.create(
                fits_file=fits_file,
                file_path=file_path,
                file_name=file_name,
                image_type=image_maker.image_type,
                description=desc,
                frame=image_maker.frame,
                ref_pixel_x=image_maker.ref_pixel_x,
                ref_pixel_y=image_maker.ref_pixel_y,
                # width  = fits_file["naxis1"],
                # height  = fits_file["naxis2"]
            )
            for arg in kwargs:
                Image_Param.create(key=arg, value=kwargs[arg])

            im.get_hash()
            return im
        else:
            return None

    def correct_file_path(self):
        self.file_path = prepend_root(
            format_string(
                Config[f"img_file_name_format"],
                self,
                sol_standard=self.fits_file.sol_standard,
                file_type=self.image_type,
            )
        )
        self.file_path = self.file_path.replace(":", "-")
        self.save()

    def get_world_from_pixels(self, x, y):
        header_dict = FileHeader(self.fits_file.get_header_as_dict())
        fake_map = Map(np.zeros((1, 1)), header_dict)
        return fake_map.pixel_to_world(x * u.pix, y * u.pix)

    def __repr__(self):
        return f"""<image:{self.type}|{self.file_path}"""

    def __str__(self):
        return f""" 
Type            = {self.image_type}
File_Path       = {self.file_path}
Hash            = {self.file_hash}
            """


class Image_Param(Base_Model):
    image = pw.ForeignKeyField(Image_File, backref="image_param")
    key = pw.CharField()
    value = pw.CharField()
