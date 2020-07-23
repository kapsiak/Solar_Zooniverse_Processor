from .base_visual import Visual_Builder
import sunpy.map as sm
from pathlib import Path
import matplotlib.animation as animation


class Basic_Video(Visual_Builder):
    visual_type = "video"
    generator_name = "basic_video"

    def __init__(self, im_type):
        super().__init__(im_type)
        self.ani = None

    def save_visual(self, save_path, clear_after=True):
        Writer = animation.writers["ffmpeg"]
        writer = Writer(fps=10, metadata=dict(artist="SunPy"), bitrate=1800)
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        self.ani.save(save_path, writer=writer)

    def create(self, file_list, **kwargs):
        maps = [sm.Map(path) for path in file_list]
        seq = sm.mapsequence.MapSequence(maps, sequence=True)
        self.fig.set_size_inches(5, 4)
        self.ani = seq.plot()
        return True
