import csv
import peewee as pw
from solar.common.config import Config
from pathlib import Path
from sunpy.map import Map
import astropy.units as u
from sunpy.io.header import FileHeader
import numpy as np
from .base_models import File_Model, Base_Model
from .fits_file import Fits_File
from typing import Any
from solar.database.utils import dbformat, dbroot
from solar.common.printing import chat


class Visual_File(File_Model):
    """
    The table to store visual files. Also includes the necessary functions to extract 
    world coordinates from coordinate on the image
    """

    visual_type = pw.CharField()

    description = pw.CharField(default="NA")

    # The following 4 float fields hold the normalized image coordinate describing the location of the actual image on the picture.
    #
    #                                           Actual Image             (1,1)
    #                       ^  +------------------------------------------+
    #                       |  |                                          |
    #    +------->          |  |       +-------------------------------+  |
    #    |                  |  |       |                               |  |
    #    |                  |  |       |                               |  |
    #    |                  |  |       |                               |  |
    #    |          Height  |  |       |                               |  |
    #    |            in    |  |       |                               |  |
    #    | im_ur_y  Pixels  |  |       |         Solar Picture         |  |
    #    |                  |  |       |                               |  |
    #    |                  |  |       |                               |  |
    #    |                  |  |       |                               |  |
    #    |                  |  |       |                               |  |
    #    |                  |  |       |                               |  |
    #    |                  |  |       |                               |  |
    #    |          +-->    |  |       +-------------------------------+  |
    #    |          |       |  |                                          |
    #    |  im_ll_y |       |  |                                          |
    #    +          +       +  +------------------------------------------+
    #                        (0,0)
    #                          +------------------------------------------>
    #                                          Width in pixels
    #                                   ^
    #                          +--------+
    #                            im_ll_x                               ^
    #                                         im_ur_x                  |
    #                          +---------------------------------------+
    #
    #
    # This scheme allows, along with the header data of the fits file that generated
    # the image, a strnslation between point on the actual picture, and point in
    # in the world

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
            event_id=fits.event.event_id,
            **kwargs,
        )
        return file_path

    @staticmethod
    def create_new_visual(
        input_file: Any,
        visual_builder: Any,
        file_name=None,
        save_format: str = Config.storage_path.img,
        desc: str = "",
        overwrite=True,
        **kwargs,
    ):

        if not isinstance(input_file, Fits_File):
            visual_type = "video"
            chat("Looks like you want me to create a video")
        else:
            visual_type = "image"
            chat("Looks like you want me to create an image")

        if visual_type == "video":
            fits_file = input_file[0]
            source_path = [x.file_path for x in input_file]
        else:
            fits_file = input_file
            source_path = fits_file.file_path

        if not file_name:
            chat(
                "Since you have not given me a file name, I am going to base it off the given fits image"
            )
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
                visual_type=visual_builder.visual_type,
                description=desc,
                im_ll_x=visual_builder.im_ll_x,
                im_ll_y=visual_builder.im_ll_y,
                im_ur_x=visual_builder.im_ur_x,
                im_ur_y=visual_builder.im_ur_y,
                width=visual_builder.width,
                height=visual_builder.height,
            )
            already_exists = False
            chat(
                "I couldn't find an existing image, so I am going to create a new one."
            )

        except Exception as e:
            print(e)
        if not already_exists or overwrite:
            if visual_builder.create(source_path, **kwargs):
                if overwrite and already_exists:
                    chat(
                        "This image already exists, but since you have set overwrite, I am going to replace the old image with a new one"
                    )
                elif not already_exists:
                    chat(
                        "It doesn't look like this image exists, so I am going to create a new one"
                    )
                to_pass = dict(
                        #extra_annot=f"{fits_file['naxis1']}"
                        )
                visual_builder.save_visual(file_path, **to_pass)
                im.file_path = file_path
                im.file_name = file_name
                im.visual_type = visual_builder.visual_type
                im.description = desc
                im.im_ll_x = visual_builder.im_ll_x
                im.im_ll_y = visual_builder.im_ll_y
                im.im_ur_x = visual_builder.im_ur_x
                im.im_ur_y = visual_builder.im_ur_y
                im.width = visual_builder.width
                im.height = visual_builder.height


                im.save()
                if visual_type == "image":
                    join = Visual_File.__get_create_join(im, fits_file)
                    join.save()
                elif visual_type == "video":
                    joins = Visual_File.__get_joins(im, input_file)
                    for j in joins:
                        j.save()

                im.get_hash()
            else:
                print("For some reason the visual failed to be created")
                return None
        return im

    @staticmethod
    def __get_joins(vis, fits):
        return [Visual_File.__get_create_join(vis, x) for x in fits]

    @staticmethod
    def __get_create_join(vis, fits):
        from .join_vis_fit import Join_Visual_Fits

        try:
            join = Join_Visual_Fits.get(
                Join_Visual_Fits.fits_file == fits, Join_Visual_Fits.visual_file == vis
            )
            chat(
                f"I found an existing join from this visual (id = {vis.id}) to the fits file id={fits.id}, so I am going to use it"
            )
        except pw.DoesNotExist:
            join = Join_Visual_Fits(fits_file=fits, visual_file=vis)
            chat(
                f"I could not find an existing visual for fits file with id {fits.id}, so I am creating a new one"
            )
        return join

    def world_from_pixel(self, x, y):
        if x > 1 and y > 1:
            return self.__world_from_pixel_abs(x, y)
        else:
            return self.__world_from_pixel_norm(x, y)

    def __world_from_pixel_abs(self, x: int, y: int):
        return self.__world_from_pixels_norm(x / self.width, y / self.height)

    def __world_from_pixels_norm(self, x: float, y: float) -> Any:
        y = 1 - y
        fits = self.fits_join.get().fits_file
        fits_width = fits["naxis1"]
        fits_height = fits["naxis2"]

        axis_x_normalized = (x - self.im_ll_x) / (self.im_ur_x - self.im_ll_x)
        axis_y_normalized = (y - self.im_ll_y) / (self.im_ur_y - self.im_ll_y)

        pix_x = axis_x_normalized * fits_width
        pix_y = axis_y_normalized * fits_height

        header_dict = FileHeader(fits.get_header_as_dict())
        fake_map = Map(np.zeros((1, 1)), header_dict)
        return fake_map.pixel_to_world(pix_x * u.pix, pix_y * u.pix)

    def get_fits(self):
        found = Visual_File.fits_join
        return list(found)

    def __repr__(self) -> str:
        return f"""<image:{self.type}|{self.file_path}"""

    def __str__(self) -> str:
        return f""" 
Type            = {self.visual_type}
File_Path       = {self.file_path}
Hash            = {self.file_hash}
            """

    def __getitem__(self, key):
        return fits_join.get().fits[key]

    @staticmethod
    def zooniverse_export(files, export_dir="export"):
        export = Path("export")
        files_dir = export
        files_dir.mkdir(exist_ok=True, parents=True)
        data = []
        header = [
            "file_path",
            "visual_type",
            "description",
            "im_ll_x",
            "im_ll_y",
            "im_ur_x",
            "im_ur_y",
            "width",
            "height",
        ]
        try:
            for image in files:
                print(image)
                new_path = image.export(files_dir)
                new_row = {
                    "file_path": str(Path(new_path).relative_to(export)),
                    "visual_type": image.visual_type,
                    "description": image.description,
                    "im_ll_x": image.im_ll_x,
                    "im_ll_y": image.im_ll_y,
                    "im_ur_x": image.im_ur_x,
                    "im_ur_y": image.im_ur_y,
                    "width": image.width,
                    "height": image.height,
                }
                data.append(new_row)
        except Exception as e:
            print(e)

        with open(export / "meta.csv", "w") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            for row in data:
                writer.writerow(row)


class Visual_Param(Base_Model):
    visual = pw.ForeignKeyField(Visual_File, backref="image_param")
    key = pw.CharField()
    value = pw.CharField()
