from dataclasses import dataclass, field
from astropy.coordinates import SkyCoord
from typing import List, Tuple
import astropy.units as u
from sunpy.io.header import FileHeader
from sunpy.map import Map
import json


@dataclass
class ZBase:
    subject_id: int = 0
    user_id: int = 0
    workflow_id: int = 0
    class_id: int = 0

    fits_id: int = -1
    visual_id: int = -1
    frame: int = -1

    purpose: str = None

    width: float = -1
    height: float = -1

    im_ll_x: float = -1
    im_ll_y: float = -1
    im_ur_x: float = -1
    im_ur_y: float = -1

    s_map: Map = None

    def as_data(self):
        return list((getattr(self, x) for x in self.data_members))


@dataclass
class ZBool(ZBase):
    data_members: Tuple[str] = field(default=("val",), init=False, repr=False)
    val: bool = False


@dataclass
class ZSpatial(ZBase):
    data_members: Tuple[str] = field(default=("x", "y"), init=False, repr=False)
    x: float = -1
    y: float = -1

    def scale(self, h, w):
        self.x = self.x / float(w)
        self.y = self.y / float(h)
        return self


@dataclass
class ZRect(ZSpatial):
    data_members: Tuple[str] = field(
        default=("x", "y", "w", "h", "a"), init=False, repr=False
    )
    w: float = -1
    h: float = -1
    a: float = -1

    def scale(self, w, h):
        super().scale(w, h)
        self.w = self.w / float(w)
        self.h = self.h / float(h)
        return self


@dataclass
class ZPoint(ZSpatial):
    pass
