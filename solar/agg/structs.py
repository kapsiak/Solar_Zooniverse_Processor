from dataclasses import dataclass
from solar.database.tables.fits_file import Fits_File
from solar.database.tables.visual_file import Visual_File
from datetime import datetime, timedelta
from solar.zooniverse.structs import ZPoint, ZRect


TIME_START = datetime(2000, 1, 1, 0, 0, 0)


def since_start(time):
    return (time - TIME_START) / timedelta(milliseconds=1)


@dataclass
class Space_Obj:
    subject_id: int = 0
    user_id: int = 0
    workflow_id: int = 0
    class_id: int = 0

    fits_id: int = -1
    visual_id: int = -1
    frame: int = -1

    time: datetime = datetime(1990, 1, 1)

    x: float = -1
    y: float = -1

    purpose: str = None

    def make_data(self):
        raise NotImplementedError

    def __set_time(self, z_struct):
        f = Fits_File.get(Fits_File.id == self.fits_id)
        self.time = f.image_time

    def __set_hpcxy(self, z_struct):
        v = Visual_File.get(Visual_File.id == self.visual_id)
        coord = v.world_from_pixel(z_struct.x, z_struct.y)
        self.y, self.x = coord.spherical.lat.arcsec, coord.spherical.lon.arcsec

    @classmethod
    def base_make(cls, z_struct):
        new = cls(
            subject_id=z_struct.subject_id,
            user_id=z_struct.user_id,
            workflow_id=z_struct.workflow_id,
            class_id=z_struct.class_id,
            fits_id=z_struct.fits_id,
            visual_id=z_struct.visual_id,
            frame=z_struct.frame,
        )
        new.__set_hpcxy(z_struct)
        new.__set_time(z_struct)
        return new

    @staticmethod
    def make(z_struct):
        if isinstance(z_struct, ZPoint):
            return Space_Point.make(z_struct)
        if isinstance(z_struct, ZRect):
            return Space_Rect.make(z_struct)
        return None


@dataclass
class Space_Point(Space_Obj):
    def make_data(self):
        return (self.x, self.y, since_start(self.time))

    @classmethod
    def make(cls, z_struct):
        return super().base_make(z_struct)


@dataclass
class Space_Rect(Space_Obj):
    w: float = -1
    h: float = -1
    a: float = -1

    def make_data(self):
        return (self.x, self.y, self.w, self.h, self.a, since_start(self.time))

    @classmethod
    def make(cls, z_struct):
        new = super().base_make(z_struct)
        new.w, new.h, new.a = z_struct.w, z_struct.h, z_struct.a
        return new
