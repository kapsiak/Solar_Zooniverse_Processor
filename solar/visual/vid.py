from .base_visual import Visual_Builder
import sunpy.map as sm
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Video_Builder(Visual_Builder):
    def __init__(self, im_type):
        super().__init__(im_type)
        self.fig = None
        self.ax = None
        self.map = None
        self.ani = None

    def save_visual(self, save_path, clear_after=True):
        Writer = animation.writers["ffmpeg"]
        writer = Writer(fps=10, metadata=dict(artist="SunPy"), bitrate=1800)
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        print("Here")
        self.ani.save(save_path, writer=writer, bbox_inches="tight")

    def create(self, file_list, **kwargs):
        maps = [sm.Map(path) for path in file_list]
        seq = sm.mapsequence.MapSequence(maps, sequence=True)
        self.ani = seq.plot()
        self.fig = plt.tight_layout()
        return True
