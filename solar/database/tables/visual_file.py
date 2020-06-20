import peewee as pw
from solar.common.config import Config
from pathlib import Path
from sunpy.map import Map
import astropy.units as u
from sunpy.io.header import FileHeader
import numpy as np
from .base_models import File_Model, Base_Model
from .fits_file import Fits_File
from typing import Union, Any, List
from solar.database.utils import dbformat, dbroot
from solar.common.printing import chat
import matplotlib.pyplot as plt


class Visual_File(File_Model):

    visual_type = pw.CharField(default="png")

    description = pw.CharField(default="NA")

    im_ll_x = pw.FloatField(default=0)
    im_ll_y = pw.FloatField(default=0)
    im_ur_x = pw.FloatField(default=0)
    im_ur_y = pw.FloatField(default=0)
    width = pw.FloatField(default=0)
    height = pw.FloatField(default=0)

    @staticmethod
    @dbroot
    def __make_path(fits, image_maker, save_format, file_name=None, **kwargs):
        file_path = dbformat(
            save_format,
            fits,
            file_name=file_name,
            image_type=image_maker.visual_type,
            **kwargs,
        )
        return file_path

    @staticmethod
    def create_new_visual(
        input_data: Any,
        visual_builder: Any,
        file_name=None,
        save_format: str = Config.storage_path.img,
        desc: str = "",
        overwrite=True,
        **kwargs,
    ):
        if isinstance(input_data, Fits_File):
            return Visual_File.create_new_image(
                input_data,
                visual_builder,
                file_name,
                save_format,
                desc,
                overwrite,
                **kwargs,
            )
        else:
            return Visual_File.create_new_video(
                input_data,
                visual_builder,
                file_name,
                save_format,
                desc,
                overwrite,
                **kwargs,
            )

    @staticmethod
    def create_new_image(
        fits_file: Union[Path, str],
        visual_builder: Any,
        file_name=None,
        save_format: str = Config.storage_path.img,
        desc: str = "",
        overwrite=True,
        **kwargs,
    ):
        # TODO: This whole thing is a bit of a mess #
        # TODO: Need to work on dealing with extension: <16-06-20> #
        if not file_name:
            file_name = fits_file.file_name
            file_name = Path(file_name).stem
        file_name = str(Path(file_name).with_suffix("." + visual_builder.visual_type))
        file_path = str(
            Visual_File.__make_path(
                fits_file, visual_builder, save_format, file_name=file_name
            )
        )
        already_exists = False
        try:
            im = Visual_File.get(Visual_File.file_path == file_path)
            already_exists = True
            

            chat("Looks like there is already a image at this filepath")

        except pw.DoesNotExist:
            im = Visual_File(
                file_path=file_path,
                file_name=file_name,
                image_type=visual_builder.visual_type,
                description=desc,
                im_ll_x=visual_builder.im_ll_x,
                im_ll_y=visual_builder.im_ll_y,
                im_ur_x=visual_builder.im_ur_x,
                im_ur_y=visual_builder.im_ur_y,
                width=visual_builder.width,
                height=visual_builder.height,
            )
            chat("I couldn't find an existing image")
        except Exception as e:
            print(e)
        if not already_exists or overwrite:
            if visual_builder.create(fits_file.file_path, **kwargs):
                chat(
                    "Since you have set overwrite, I am going to replace the old image with a new one"
                )
                visual_builder.save_visual(file_path)
                im.file_path=file_path
                im.file_name=file_name
                im.image_type=visual_builder.visual_type
                im.description=desc
                im.im_ll_x=visual_builder.im_ll_x
                im.im_ll_y=visual_builder.im_ll_y
                im.im_ur_x=visual_builder.im_ur_x
                im.im_ur_y=visual_builder.im_ur_y
                im.width=visual_builder.width
                im.height=visual_builder.height

                im.save()
                join = Visual_File.get_create_join(im, fits_file)
                join.save()
                im.get_hash()
            else:
                return None
        return im

    @staticmethod
    def create_new_video(
        files,
        visual_builder: Any,
        file_name=None,
        save_format: str = Config.storage_path.img,
        desc: str = "",
        overwrite=True,
        **kwargs,
    ):
        # TODO: This whole thing is a bit of a mess #
        # TODO: Need to work on dealing with extension: <16-06-20> #
        if not file_name:
            file_name = files[0].file_name
            file_name = Path(file_name).stem
        file_name = str(Path(file_name).with_suffix("." + visual_builder.visual_type))
        file_path = str(
            Visual_File.__make_path(
                files[0], visual_builder, save_format, file_name=file_name
            )
        )
        already_exists = False
        try:
            im = Visual_File.get(Visual_File.file_path == file_path)
            already_exists = True
            chat("Looks like there is already an image at this filepath")

        except pw.DoesNotExist:
            im = Visual_File(
                file_path=file_path,
                file_name=file_name,
                image_type=visual_builder.visual_type,
                description=desc,
                im_ll_x=visual_builder.im_ll_x,
                im_ll_y=visual_builder.im_ll_y,
                im_ur_x=visual_builder.im_ur_x,
                im_ur_y=visual_builder.im_ur_y,
                width=visual_builder.width,
                height=visual_builder.height,
            )
            chat("I couldn't find an existing image")
        except Exception as e:
            print(e)
        if not already_exists or overwrite:
            if visual_builder.create([f.file_path for f in files], **kwargs):
                chat(
                    "Since you have set overwrite, I am going to replace the old image with a new one"
                )
                visual_builder.save_visual(file_path)

                im.save()
                for f in files:
                    join = Visual_File.get_create_join(im, f)
                    join.save()
                im.get_hash()
            else:
                return None
        return im

    @staticmethod
    def get_create_join(vis, fits):
        from .join_vis_fit import Join_Visual_Fits

        try:
            join = Join_Visual_Fits.get(
                Join_Visual_Fits.fits_file == fits, Join_Visual_Fits.visual_file == vis
            )
        except pw.DoesNotExist:
            join = Join_Visual_Fits(fits_file=fits, visual_file=vis)
        return join

    def get_world_from_pixel(self,x,y):
        if x>1 and y >1:
            return self.__get_world_from_pixel_abs(x, y)
        else:
            return self.__get_world_from_pixel_norm( x, y)

       
    def __get_world_from_pixel_abs(self, x:int, y:int):
        return self.__get_world_from_pixels_norm(x/self.width, y/self.height)

    def __get_world_from_pixels_norm(self, x: float, y: float) -> Any:
        y = 1 - y
        fits =  self.fits_join.get().fits_file
        fits_width =   fits["naxis1"]
        fits_height =   fits["naxis2"]
        
        axis_x_normalized = (x-self.im_ll_x)/(self.im_ur_x- self.im_ll_x)
        axis_y_normalized = (y-self.im_ll_y)/(self.im_ur_y- self.im_ll_y)

        pix_x = axis_x_normalized * fits_width
        pix_y = axis_y_normalized * fits_height

        header_dict = FileHeader(fits.get_header_as_dict())
        fake_map = Map(np.zeros((1, 1)), header_dict)
        return fake_map.pixel_to_world(pix_x * u.pix, pix_y * u.pix)

    def __repr__(self) -> str:
        return f"""<image:{self.type}|{self.file_path}"""

    def __str__(self) -> str:
        return f""" 
Type            = {self.image_type}
File_Path       = {self.file_path}
Hash            = {self.file_hash}
            """


class Visual_Param(Base_Model):
    visual = pw.ForeignKeyField(Visual_File, backref="image_param")
    key = pw.CharField()
    value = pw.CharField()
