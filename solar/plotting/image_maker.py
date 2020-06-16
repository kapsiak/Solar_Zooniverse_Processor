import matplotlib.pyplot as plt
import sunpy.map as sm
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from pathlib import Path


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

    def save_image(self, save_path):
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        self.fig.savefig(save_path, transparent=False, dpi=300)

    def create(self, file_path):
        pass


class Unframed_Image(Image_Maker):
    def __init__(self, im_type):
        print(im_type)
        super().__init__(im_type)
        print(self.image_type)
        self.frame = False

    def create(self, file_path, cmap="hot", size=3):
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
        self.ax.imshow(self.map.data, aspect="equal")


class Basic_Image(Image_Maker):
    def __init__(self, im_type):
        super().__init__(im_type)
        self.frame = False

    def create(self, file_path, cmap="hot", size=3):
        self.map = sm.Map(file_path)
        self.fig = plt.figure()
        self.map.plot()
