import peewee as pw
from solar.common.config import Config
from pathlib import Path
from sunpy.map import Map
import astropy.units as u
from sunpy.io.header import FileHeader
import numpy as np
from .base_models import File_Model
from .fits_file import Fits_File
from typing import Any
from solar.database.utils import dbformat, dbroot, dbpathformat
from solar.common.printing import chat
from solar.visual.img import Image_Builder
from solar.visual.vid import Video_Builder
import solar.common.mapproc as mp
import datetime


class Visual_File(File_Model):

    """
    The table to store visual files. Also includes the necessary functions to extract
    world coordinates from coordinate on the image


    Sorry, this class is a bit of a mess, I probably should have made separate functions to create the images.
    """

    
    file_name_format = Config.file_storage.img
    file_path_format = Config.storage_path.img

    #: The type of visual (either image for video)
    visual_type = pw.CharField()

    #: The extension of the file
    extension = pw.CharField()

    #: The generator used to create the visual
    visual_generator = pw.CharField(null=True)

    #: An optional description of the generated visual
    description = pw.CharField(default="NA")

    #: The time the visual was generated
    time_generated = pw.DateTimeField(default=datetime.datetime.now)

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
    def create_new_visual(
        input_file: Any,
        visual_builder: Any,
        save_format: str = Config.storage_path.img,
        file_name_format: str = Config.file_storage.img,
        desc: str = "",
        overwrite=True,
    ):
        """
        Create a new visual. This is a wrapper that uses a :class:`~solar.visual.base_visual.Visual_Builder` to create new files and automatically add them to the database.

        Information about the actual image generation can be found in :doc:`/visuals/index`.

        :param input_file: The :class:`~solar.database.tables.fites_file.Fits_File` to be used in generating the images.
        :type input_file: Either a list or a single :class:`~solar.database.tables.fites_file.Fits_File`
        :param visual_builder: The :class:`~solar.visual.base_visual.Visual_Builder` to use to generate the images
        :type visual_builder: :class:`~solar.visual.base_visual.Visual_Builder`
        :param save_format: The format to save the files
        :type save_format: str
        :param file_save_format: The format for the file name
        :type save_format: str
        :param desc: Optional Description
        :type save_format: str
        :param overwrite: Whether to overwrite existing files. If true aborts if a file that elready exists would be generated
        :type save_format: bool
        """
        btype = type(visual_builder)
        if issubclass(btype, Video_Builder):
            chat("Looks like you want me to create a video")
            return Visual_File.__create_new_video(
                input_file,
                visual_builder,
                save_format,
                file_name_format,
                desc,
                overwrite,
            )

        if issubclass(btype, Image_Builder):
            if isinstance(input_file, Fits_File):
                chat("Looks like you want me to create an image")
                return Visual_File.__create_new_image(
                    input_file,
                    visual_builder,
                    save_format,
                    file_name_format,
                    desc,
                    overwrite,
                )
            else:
                chat("Looks like you want me to create several images image")
                return [
                    Visual_File.__create_new_image(
                        x,
                        visual_builder,
                        save_format,
                        file_name_format,
                        desc,
                        overwrite,
                    )
                    for x in input_file
                ]

    @staticmethod
    def __make_fname(fits, image_maker):
        file_name = Path(fits.file_name).stem
        file_name = str(Path(file_name).with_suffix("." + image_maker.extension))
        return file_name

    @staticmethod
    def __make_path_name(fits, image_maker, save_format, file_name):
        file_path = dbformat(
            save_format,
            fits,
            file_name=file_name,
            extension=image_maker.extension,
            event_id=fits.event.event_id,
        )
        return dbroot(file_path)

    @staticmethod
    def __delete(im):
        for x in im.fits_join:
            x.delete_instance()

        im.delete_instance()

    @staticmethod
    def __try_create_visual(file_path, file_name, visual_builder, desc):
        try:
            im = Visual_File.get(Visual_File.file_path == file_path)
            already_exists = True
            chat("Looks like there is already a image at this file path")

        except pw.DoesNotExist:
            im = Visual_File(
                file_path=file_path,
                file_name=file_name,
                visual_type=visual_builder.visual_type,
                visual_generator=visual_builder.generator_name,
                extension=visual_builder.extension,
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
            im = None
            already_exists = False
            print(e)

        return (im, already_exists)

    @staticmethod
    def __report_status(name, exists, overwrite):
        if exists and not overwrite:
            chat(
                f"This {name} exists and overwrite is false, so I am not going to continue"
            )
            return False

        if exists and overwrite:
            chat(
                f"This {name} seems to already exist, but since you have selected overwrite, I am going to replace it with a new one"
            )

            return True

        if not exists:
            chat(f"This {name} doesn't seem to exist, so I am creating a new one")
            return True

    def __assign_generated_parameters(self, visual_builder):
        self.im_ll_x = visual_builder.im_ll_x
        self.im_ll_y = visual_builder.im_ll_y
        self.im_ur_x = visual_builder.im_ur_x
        self.im_ur_y = visual_builder.im_ur_y
        self.width = visual_builder.width
        self.height = visual_builder.height
        return self

    @staticmethod
    def __create_new_image(
        input_file: Any,
        visual_builder: Any,
        save_format: str = Config.storage_path.img,
        file_name_format: str = Config.file_storage.img,
        desc: str = "",
        overwrite=True,
    ):

        base_fits = input_file

        file_name = dbformat(file_name_format, base_fits, visual_builder)
        print(base_fits.file_name.stem)
        full_path = dbpathformat(
            file_name_format, save_format, base_fits, visual_builder, base_fits.event
        )

        im, exists = Visual_File.__try_create_visual(
            full_path, file_name, visual_builder, desc
        )
        source_path = base_fits.file_path

        if not Visual_File.__report_status("image", exists, overwrite):
            return None

        created = visual_builder.create(source_path)

        if not created:
            return None

        visual_builder.save_visual(base_fits, full_path)

        im.__assign_generated_parameters(visual_builder)
        im.save()

        join = Visual_File.__get_create_join(im, base_fits)
        join.save()

        im.get_hash()

        return im

    @staticmethod
    def __create_new_video(
        input_files: Any,
        visual_builder: Any,
        save_format: str = Config.storage_path.img,
        file_name_format: str = Config.file_storage.img,
        desc: str = "",
        overwrite=True,
        base_fits=None,
    ):
        base_fits = base_fits if base_fits else input_files[0]
        file_name = dbformat(file_name_format, base_fits, visual_builder)
        full_path = dbpathformat(
            file_name_format, save_format, base_fits, visual_builder, base_fits.event
        )
        im, exists = Visual_File.__try_create_visual(
            full_path, file_name, visual_builder, desc
        )
        source_paths = [x.file_path for x in input_files]

        if not Visual_File.__report_status("video", exists, overwrite):
            return None

        created = visual_builder.create(source_paths)

        if not created:
            return None

        visual_builder.save_visual(base_fits, full_path)

        im.__assign_generated_parameters(visual_builder)
        im.set_visual_hash()
        im.save()

        joins = Visual_File.__get_joins(im, input_files)
        for j in joins:
            j.save()
        im.get_hash()

        return im

    @staticmethod
    def __get_joins(vis, fits):
        return [Visual_File.__get_create_join(vis, x) for x in fits]

    @staticmethod
    def __get_create_join(vis, fits):
        from .join_vis_fit import Join_Visual_Fits

        try:
            join = (
                Join_Visual_Fits.select()
                .join(Visual_File)
                .where(
                    Join_Visual_Fits.fits_file == fits,
                    Join_Visual_Fits.visual_file == vis,
                    Visual_File.file_hash == vis.file_hash,
                )
                .get()
            )
            chat(
                f"I found an existing join from this visual (id = {vis.id}) to the fits file id={fits.id}, so I am going to use it. Both images has a file hash {vis.file_hash}."
            )
        except pw.DoesNotExist:
            join = Join_Visual_Fits(fits_file=fits, visual_file=vis)
            chat(
                f"I could not find an existing visual for fits file with id {fits.id}, so I am creating a new one"
            )
        # join = Join_Visual_Fits(fits_file=fits, visual_file=vis)
        return join

    def pixel_from_world(self, hpc_x, hpc_y, normalized=False):
        """ Get the pixel coordinate from a world coordinate
        """
        fits = self.fits_join.get().fits_file
        header_dict = FileHeader(fits.get_header_as_dict())
        fake_map = Map(np.zeros((1, 1)), header_dict)
        return mp.pixel_from_world(fake_map, self, hpc_x, hpc_y, normalized=normalized)

    def world_from_pixel(self, x, y):
        """ Get a world coordinate from a pixel on the image.
        
        :rtype: sunpy coordinate
        """
        if x > 1 and y > 1:
            return self.__world_from_pixel_abs(x, y)
        else:
            return self.__world_from_pixel_norm(x, y)

    def world_from_pixel_value(self, x, y):
        """Returns the HPC coordinate from a pixel coordinate as a tuple.
        """
        v = self.world_from_pixel(x, y)
        return v.spherical.lon.arcsec, v.spherical.lat.arcsec

    def __world_from_pixel_abs(self, x: int, y: int):
        return self.__world_from_pixel_norm(x / self.width, y / self.height)

    def __world_from_pixel_norm(self, x: float, y: float) -> Any:
        fits = self.fits_join.get().fits_file
        header_dict = FileHeader(fits.get_header_as_dict())
        fake_map = Map(np.zeros((1, 1)), header_dict)

        return mp.world_from_pixel_norm(fake_map, self, x, y)

    def get_fits(self):
        """
        Get the fits files used to generate this image
        """
        from .join_vis_fit import Join_Visual_Fits

        found = Join_Visual_Fits.select().where(Join_Visual_Fits.visual_file == self)
        return list(found)

    def __repr__(self) -> str:
        return f"""<vid: {self.id}>"""

    def __str__(self) -> str:
        return f""" 
Type            = {self.visual_type}
File_Path       = {self.file_path}
Hash            = {self.file_hash}
            """

    def __set_vis_hash(self):
        self.visual_hash = hash(
            (
                self.extension,
                self.visual_generator,
                self.im_ll_x,
                self.im_ll_y,
                self.im_ur_x,
                self.im_ur_y,
                self.width,
                self.height,
            )
        )
