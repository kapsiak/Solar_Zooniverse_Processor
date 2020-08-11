from dataclasses import dataclass, field
from astropy.coordinates import SkyCoord
from typing import List, Tuple
import astropy.units as u
from sunpy.io.header import FileHeader
from sunpy.map import Map
import json
import numpy as np


def r(x):
    return round(x, 2)


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

    _fits_dict: dict = None

    @property
    def fits_dict(self):
        return self._fits_dict

    @fits_dict.setter
    def fits_dict(self, data):
        # header_dict = FileHeader(data)
        # fake_map = Map(np.zeros((1, 1)), header_dict)
        self._fits_dict = data

    def as_data(self):
        return list((getattr(self, x) for x in self.data_members))

    def __str__(self):
        if type(self) == ZBase:
            return f"{self.__class__.__name__}({self.subject_id})"
        return f"{self.__class__.__name__}({self.subject_id}" + ", {})"


@dataclass
class ZBool(ZBase):
    data_members: Tuple[str] = field(default=("val",), init=False, repr=False)
    val: bool = False

    def __str__(self):
        return super().__str__().format(self.val)


@dataclass
class ZSpatial(ZBase):
    data_members: Tuple[str] = field(default=("x", "y"), init=False, repr=False)
    x: float = -1  # x coord in image coordinates of the center of the rectangle
    y: float = -1  # y coord in image coordinates of the center of the rectangle

    width: float = -1   # width of the image in pixels
    height: float = -1  # height of the image in pixels

    im_ll_x: float = -1  # x location of lower left corner of the actual solar image
    im_ll_y: float = -1  # y location of lower left corner of the actual solar image
    im_ur_x: float = -1  # x location of upper right corner of the actual solar image
    im_ur_y: float = -1  # x location of upper right corner of the actual solar image

    def __str__(self):
        if type(self) in (ZSpatial, ZPoint):
            return super().__str__().format(f"{r(self.x),r(self.y)}")
        return super().__str__().format(f"{r(self.x),r(self.y)}, " + "{}")


@dataclass
class ZRect(ZSpatial):
    data_members: Tuple[str] = field(
        default=("x", "y", "w", "h", "a"), init=False, repr=False
    )
    w: float = -1 # width of the rectangle in image coords
    h: float = -1 # height of the rectangle in image coords
    a: float = -1 # angle of the rectangle relative to the x axis

    def __str__(self):
        return super().__str__().format(f"{r(self.w),r(self.h)}")


@dataclass
class ZPoint(ZSpatial):
    pass
