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
    #: Which members get exported when using the method :meth:`as_data`
    data_members: Tuple[str] = None

    #: The subject ID
    subject_id: int = 0
    #: The user who made this classification
    user_id: int = 0
    #: The ID of the workflow for this classification
    workflow_id: int = 0
    #: The ID of this classification
    class_id: int = 0

    #: The ID of the fits file used to generate the image used in this classification
    fits_id: int = -1
    #: The ID of the visual file used in this classification
    visual_id: int = -1
    #: The frame of this classification
    frame: int = -1

    #: The purpose of this data
    purpose: str = None

    #: The dictionary containing the fits header data of the fits file used to generate the image
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
        """ Get the this structure as a list of data.

        :returns: A list of data as described in :attr:`data_members`
        """
         
        return list((getattr(self, x) for x in self.data_members))

    def __str__(self):
        if type(self) == ZBase:
            return f"{self.__class__.__name__}({self.subject_id})"
        return f"{self.__class__.__name__}({self.subject_id}" + ", {})"


@dataclass
class ZBool(ZBase):
    data_members: Tuple[str] = field(default=("val",), init=False, repr=False)

    #: Whether the boolean is true or false
    val: bool = False

    def __str__(self):
        return super().__str__().format(self.val)


@dataclass
class ZSpatial(ZBase):
    data_members: Tuple[str] = field(default=("x", "y"), init=False, repr=False)

    x: float = -1  #: x coord in image coordinates of the center of the rectangle or the point
    y: float = -1  #: y coord in image coordinates of the center of the rectangle or the point

    width: float = -1  #: width of the image in pixels
    height: float = -1  #: height of the image in pixels

    im_ll_x: float = -1  #: x location of lower left corner of the actual solar image
    im_ll_y: float = -1  #: y location of lower left corner of the actual solar image
    im_ur_x: float = -1  #: x location of upper right corner of the actual solar image
    im_ur_y: float = -1  #: x location of upper right corner of the actual solar image

    def __str__(self):
        if type(self) in (ZSpatial, ZPoint):
            return super().__str__().format(f"{r(self.x),r(self.y)}")
        return super().__str__().format(f"{r(self.x),r(self.y)}, " + "{}")


@dataclass
class ZRect(ZSpatial):
    data_members: Tuple[str] = field(
        default=("x", "y", "w", "h", "a"), init=False, repr=False
    )
    w: float = -1  #: width of the rectangle in image coords
    h: float = -1  #: height of the rectangle in image coords
    a: float = -1  #: angle of the rectangle relative to the x axis

    def __str__(self):
        return super().__str__().format(f"{r(self.w),r(self.h)}")


@dataclass
class ZPoint(ZSpatial):
    """
    At this point this is class is identical to :class:`ZSpatial`.
    """

    pass
