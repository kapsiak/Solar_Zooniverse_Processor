import matplotlib.pyplot as plt
import sunpy.map as sm
from pathlib import Path
from .base_visual import Visual_Builder
from solar.common.printing import chat
import os
import numpy as np


class Image_Builder(Visual_Builder):
    """
    Basic image builder
    """

    generator_name = "generic_image"
    visual_type = "image"

    def __init__(self, im_type, dpi=300):
        super().__init__(im_type, dpi=dpi)
        self.creation_params = None

    def generate_image_data(self):
        """Function generate_image_data: 

        Analyze the existing self.fig to get information about the image.

        :returns: None
        :type return: None
        """
        bbox = self.fig.get_window_extent().transformed(
            self.fig.dpi_scale_trans.inverted()
        )
        self.width, self.height = bbox.width * self.fig.dpi, bbox.height * self.fig.dpi
        (self.im_ll_x, self.im_ll_y), (self.im_ur_x, self.im_ur_y) = (
            self.fig.axes[0].get_position().get_points()
        )

    def save_visual(self, fits, save_path, max_size=800, clear_after=True, default_dpi=300):
        """Save this visual. If fits is none, no metadata will be generated.
        
        :param fits: The fits file used to generate the image. Used for metadata extraction.
        (This is not great practice and should probably be rewritten)
        :type fits: Fits_File
        :param save_path: The location to save the image
        :type save_path: Path-like
        :param max_size: Maximum fits file size in kilobytes, defaults to 1000.
            we use this max size to calculate the max theoretical output dpi^2*fits_size using default dpi of 300.
            if the theoretical output is greater that this max then we reduce the dpi accordingly
        :type max_size: float
        :param clear_after: Clear the image from memory after it has been saved ,defaults to True
        
        If generating a large number of images this should be set to true or there will be a memory overflow error.
        On the other hand, if manipulating a single image repeadedly, probably better to keep it around between saves.
        
        :type clear_after: bool
        :returns: None
        :type return: None
        """
        self.generate_image_data()
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        size_fits_file = os.path.getsize(fits.file_path)
                
        if fits:
            self.fig.savefig(save_path, metadata=self.generate_metadata(fits))
        else:
            self.fig.savefig(save_path)
                   
        output_max = default_dpi * default_dpi * max_size * 1000
        output_size = self.fig.dpi * self.fig.dpi * size_fits_file
        
        if output_size > output_max:
            chat("Looks like the dpi is too high, reducing")
            self.create(
                self.creation_params["fpath"],
                self.creation_params["cmap"],
                self.creation_params["size"],
                int(
                    self.creation_params["dpi"]
                    * np.sqrt(max_size*1000/size_fits_file)
                ),   
            )
            self.save_visual(fits, save_path, max_size, clear_after)
        if clear_after:
            plt.close()

    def show(self):
        plt.show()

    def _store_create_params(self, **kwargs):
        self.creation_params = kwargs


class Unframed_Image(Image_Builder):
    """
    An image with no frame
    """

    generator_name = "unframed_image"

    def __init__(self, im_type, dpi=300):
        super().__init__(im_type, dpi=dpi)
        self.frame = False

    def create(self, file_path, cmap="hot", size=None, dpi=None):
        """Create the visual in memory
        
        :param file_path: The path to the fits file
        :type file_path: str
        :param cmap: color map, defaults to "hot"
        :type cmap: str
        :param size: the size of the image, defaults to None
        :type size: float
        :param dpi: the dpi of the image, defaults to None
        :type dpi: int
        """
        if not Path(file_path).is_file():
            return False
        self.map = sm.Map(file_path)
        x = self.map.meta["naxis1"]
        y = self.map.meta["naxis2"]
        larger = max(x, y)
        self.fig = plt.figure()
        self.fig.set_size_inches((x / larger) * size, (y / larger) * size)
        self.ax = plt.Axes(self.fig, [0.0, 0.0, 1.0, 1.0])
        self.ax.set_axis_off()
        self.fig.add_axes(self.ax)
        plt.set_cmap(cmap)

        self.ax.imshow(self.map.data, aspect="equal", origin="lower")
        return True


class Basic_Image(Image_Builder):
    """
    The basic image used in the zooniverse project.
    """
    generator_name = "basic_image"

    def __init__(self, im_type, dpi=300):
        super().__init__(im_type, dpi=dpi)
        self.frame = False

    def create(self, file_path, cmap="hot", size=None, dpi=None):
        """Create the visual in memory
        
        :param file_path: The path to the fits file
        :type file_path: str
        :param cmap: color map, defaults to "hot"
        :type cmap: str
        :param size: the size of the image, defaults to None
        :type size: flaot
        :param dpi: the dpi of the image, defaults to None
        :type dpi: int
        """
        if not dpi:
            dpi = self.dpi

        # This function is here so that we can recall this function later with the
        # same parameters if we need to rescale
        self._store_create_params(fpath=file_path, cmap=cmap, size=size, dpi=dpi)

        # TODO:
        # Refractor this class so there is less stuff in the create() function.
        # <06-08-20, yourname> #
        if not issubclass(type(file_path), sm.GenericMap):
            self.map = sm.Map(file_path)
            if not Path(file_path).is_file():
                print(
                    "You are asking me to create an image from a fits file that does not exist"
                )
                return False
        else:
            self.map = file_path

        title_obsdate = self.map.date.strftime("%Y-%b-%d %H:%M:%S")

        if not size:
            self.fig = plt.figure(
                # figsize=[4.4, 4.4],
                dpi=dpi
            )
        else:
            self.fig = plt.figure(figsize=[size, size], dpi=dpi)

        self.ax = self.fig.add_subplot(1, 1, 1, projection=self.map)
        plt.sca(self.ax)
        plt.figure(self.fig.number)
        # self.fig.subplots_adjust(right = 1, left = -.2,top = 0.9, bottom=0.1)
        # self.ax.imshow(self.map.data)
        self.map.plot(origin="lower")
        self.ax.set_xlabel("Solar X (arcsec)")
        self.ax.set_ylabel("Solar Y (arcsec)")
        self.ax.set_title(f"SDO-AIA   {title_obsdate}")
        self.generate_image_data()
        self.draw_annotations()
        # self.generate_image_data()
        return True


def main():
    pass
