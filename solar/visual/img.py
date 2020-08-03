import matplotlib.pyplot as plt
import sunpy.map as sm
from pathlib import Path
from .base_visual import Visual_Builder
from solar.common.printing import chat


class Image_Builder(Visual_Builder):

    generator_name = "generic_image"
    visual_type = "image"

    def __init__(self, im_type, dpi=300):
        super().__init__(im_type, dpi=dpi)
        self.creation_params = None

    def generate_image_data(self):
        bbox = self.fig.get_window_extent().transformed(
            self.fig.dpi_scale_trans.inverted()
        )
        self.width, self.height = bbox.width * self.fig.dpi, bbox.height * self.fig.dpi
        (self.im_ll_x, self.im_ll_y), (self.im_ur_x, self.im_ur_y) = (
            self.fig.axes[0].get_position().get_points()
        )

    def save_visual(self, fits, save_path, max_size=1000, clear_after=True):
        self.generate_image_data()
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        self.fig.savefig(save_path, metadata=self.generate_metadata(fits))
        img_size = p.stat().st_size
        if img_size > max_size * 1000:
            chat("Looks like the dpi is too high, reducing")
            self.create(
                self.creation_params["fpath"],
                self.creation_params["cmap"],
                self.creation_params["size"],
                int(
                    self.creation_params["dpi"]
                    * (1 - (img_size - max_size * 1000) / img_size)
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
    generator_name = "unframed_image"

    def __init__(self, im_type, dpi=300):
        super().__init__(im_type, dpi=dpi)
        self.frame = False

    def create(self, file_path, cmap="hot", size=None, dpi=None):
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
    generator_name = "basic_image"

    def __init__(self, im_type, dpi=300):
        super().__init__(im_type, dpi=dpi)
        self.frame = False

    def create(self, file_path, cmap="hot", size=None, dpi=None):
        if not dpi:
            dpi = self.dpi

        self._store_create_params(fpath=file_path, cmap=cmap, size=size, dpi=dpi)

        if not issubclass(type(file_path), sm.GenericMap):
            self.map = sm.Map(file_path)
            if not Path(file_path).is_file():
                print(
                    "You are asking me to create an image from a fits file that does not exist"
                )
                return False
        else:
            self.map = file_path
            if not Path(file_path).is_file():
                return False

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
        self.draw_annotations()
        # self.generate_image_data()
        return True


def main():
    pass
