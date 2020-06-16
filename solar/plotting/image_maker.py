import matplotlib.pyplot as plt
import sunpy.map as sm
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from pathlib import Path

from functools import wraps


class Image_Maker:
    def __init__(self, im_type):
        self.image_type = im_type
        self.ref_pixel_x = 0
        self.ref_pixel_y = 0
        self.frame = None
        self.fig = None
        self.ax = None
        self.map = None
        self.dpi = 300

    def save_image(self, save_path, clear_after = True):
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        self.fig.savefig(save_path, transparent=False, dpi=300)
        if clear_after:
            plt.close()

    def create(self, file_path, **kwargs):
        pass


class Unframed_Image(Image_Maker):
    def __init__(self, im_type):
        super().__init__(im_type)
        self.frame = False

    def create(self, file_path, cmap="hot", size=3, **kwargs):
        if not Path(file_path).is_file():
            return False
        self.map = sm.Map(file_path)
        x = self.map.meta["naxis1"]
        y = self.map.meta["naxis2"]
        larger = max(x, y)
        self.fig = plt.figure()
        self.fig.set_size_inches(x / larger * size, y / larger * size)
        self.ax = plt.Axes(self.fig, [0.0, 0.0, 1.0, 1.0])
        self.ax.set_axis_off()
        self.fig.add_axes(self.ax)
        plt.set_cmap(cmap)

        data_stamp = kwargs.get('data_stamp', None)
        if data_stamp:
            self.ax.text(0.1,0.1,data_stamp, fontsize = 4,color='white')

        self.ax.imshow(self.map.data, aspect="equal", origin='lower')
        return True


class Basic_Image(Image_Maker):
    def __init__(self, im_type):
        super().__init__(im_type)
        self.frame = False

    def create(self, file_path, cmap="hot", size=3, **kwargs):
        if not Path(file_path).is_file():
            return False
        self.map = sm.Map(file_path)
        self.fig = plt.figure()
        self.map.plot()
        return True
