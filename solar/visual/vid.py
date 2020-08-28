from .base_visual import Visual_Builder
import sunpy.map as sm
from pathlib import Path
import matplotlib.animation as animation


class Video_Builder(Visual_Builder):

    """
    A basic video generation class. Needs lots of work, but also be unnecessary depending on zooniverse.
    """

    #: The type of visual
    visual_type = "video"
    #: The name of this generator
    generator_name = "base_video"

    def __init__(self, im_type, *args, **kwargs):
        super().__init__(im_type, *args, **kwargs)

        # The animation
        self.ani = None

    def save_visual(self, save_path, clear_after=True):
        Writer = animation.writers["ffmpeg"]
        writer = Writer(fps=10, metadata=dict(artist="SunPy"), bitrate=1800)
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        self.ani.save(save_path, writer=writer)

    def create(self, file_list):
        maps = [sm.Map(path) for path in file_list]
        seq = sm.mapsequence.MapSequence(maps, sequence=True)
        self.fig.set_size_inches(5, 4)
        self.ani = seq.plot()
        return True


class Basic_Video(Video_Builder):

    #: The name of this generator
    generator_name = "basic_video"

    def __init__(self, im_type, *args, **kwargs):
        super().__init__(im_type, *args, **kwargs)

    def save_visual(self, save_path, clear_after=True):
        """ Save the visual.        

        :param save_path: The location of the save
        :type save_path: str
        :param clear_after: Whether to remove the image from memory after saving, defaults to True
        :type clear_after: bool
        """
        Writer = animation.writers["ffmpeg"]
        writer = Writer(fps=10, metadata=dict(artist="SunPy"), bitrate=1800)
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        self.ani.save(save_path, writer=writer)

    def create(self, file_list):
        """ Create a movie from a list of fits files
        
            :param file_list: a list of fits files string
            :type file_list: List[str]
        """
        maps = [sm.Map(path) for path in file_list]
        seq = sm.mapsequence.MapSequence(maps, sequence=True)
        self.fig.set_size_inches(5, 4)
        self.ani = seq.plot()
        return True
