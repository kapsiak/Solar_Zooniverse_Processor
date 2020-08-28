from dataclasses import dataclass
from solar.database.tables.fits_file import Fits_File
from solar.database.tables.visual_file import Visual_File
from datetime import datetime, timedelta
from solar.zooniverse.structs import ZPoint, ZRect
from sunpy.map import Map
from sunpy.io.header import FileHeader
import numpy as np
from solar.common.mapproc import world_from_pixel, pixel_from_world
from solar.common.config import Config


TIME_START = datetime(1995, 1, 1, 0, 0, 0)

def make(z_struct):
    """Create an appropriate Space_Obj

    :param z_struct: Zooniverse Structure
    :type z_struct: ZBase
    :returns: Appropriate Space_Obj subclass
    :rtype: Space_Obj
    """
    if isinstance(z_struct, ZPoint):
        return Space_Point.make(z_struct)
    if isinstance(z_struct, ZRect):
        return Space_Rect.make(z_struct)
    return None


def __since_start(time):
    """
    Simple function to convert a time into a float by taking the difference between the time and TIME_START in milliseconds

    :param time: The time to convert
    :type time: Datetime
    """
    return (time - TIME_START) / timedelta(milliseconds=1)


def __r(x):
    return round(x, 2)


@dataclass
class Space_Obj:

    #: The user who made this classification
    user_id: int = 0
    #: The ID of the workflow for this classification
    workflow_id: int = 0
    #: The ID of this classification
    class_id: int = 0
    #: The subject ID
    subject_id: int = 0

    #: The ID of the fits file used to generate the image used in this classification
    fits_id: int = -1
    #: The ID of the visual file used in this classification
    visual_id: int = -1

    #: The frame of this classification
    frame: int = -1

    _time: datetime = datetime(1990, 1, 1)

    _x: float = -1
    _y: float = -1

    _smap: Map = None

    #: The purpose of this data
    purpose: str = None

    width: float = -1  #: width of the image in pixels
    height: float = -1  #: height of the image in pixels

    im_ll_x: float = -1  #: x location of lower left corner of the actual solar image
    im_ll_y: float = -1  #: y location of lower left corner of the actual solar image
    im_ur_x: float = -1  #: x location of upper right corner of the actual solar image
    im_ur_y: float = -1  #: x location of upper right corner of the actual solar image

    def __str__(self):
        if type(self) in (Space_Obj, Space_Point):
            return f"{self.__class__.__name__}({self.subject_id},{self._time}, {__r(self._x),__r(self._y)})"
        return (
            f"{self.__class__.__name__}({self.subject_id},{self._time}, {__r(self._x),__r(self._y)}"
            + ", {})"
        )

    def make_data(self):
        raise NotImplementedError

    def get_map(self, z_struct):
        """Construct a sunpy.map.Map from a given fits header. The data is irrelevant, we care only about the header.
        
        :param z_struct: Zooniverse Data Structure
        :type z_struct: None
        :returns: None
        :type return: None
        """
        if not self._smap:
            self.smap = z_struct.fits_header_data

    @property
    def smap(self):
        """
        The sunpy map containing the image header
        """
        return self._smap

    @smap.setter
    def smap(self, data):
        """Set the value of smap using a dictionary, constructs a fake smap with the desired header
        
        :param data: Dict like object from which a header may be constructs
        :type data: dict-like
        :returns: None
        :type return: None
        """
        header_dict = FileHeader(data)
        fake_map = Map(np.zeros((1, 1)), header_dict)
        self._smap = fake_map

    def as_data(self):
        """Convert class into a tuple of data suitable for aggregation

        :returns: List of data
        :type return: List[vals]
        """
        return list((getattr(self, x) for x in self.data_members))

    @property
    def time(self):
        """
        The time of the classification
        """
        return self._time

    @time.setter
    def time(self, z_struct):
        self.get_map(z_struct)
        if self.smap:
            self._time = datetime.strptime(
                self.smap.meta["date-obs"], Config.time_format.fits
            )
        else:
            try:
                f = Fits_File.get(Fits_File.id == self.fits_id)
                self._time = f.image_time
            except Exception as e:
                print(e)

    @property
    def x(self):
        """
        HPC x coordinate of the classification. 
        """
        return self._x

    @x.setter
    def x(self, z_struct):
        """Setter for x coord
        
        :param z_struct: Zooniverse import structure
        :type z_struct: ZBase
        :returns: None
        :type return: None
        """
        self.get_map(z_struct)
        if self.smap:
            coord = world_from_pixel(self.smap, z_struct, z_struct.x, z_struct.y)
            self._x = coord.spherical.lon.arcsec
        else:
            try:
                v = Visual_File.get(Visual_File.id == self.visual_id)
                coord = v.world_from_pixel(z_struct.x, z_struct.y)
                self._x = coord.spherical.lon.arcsec
            except Exception as e:
                print(e)

    @property
    def y(self):
        """
        HPC y coordinate for the classification
        """
        return self._y

    @y.setter
    def y(self, z_struct):
        """Setter for y coord
        
        :param z_struct: Zooniverse import structure
        :type z_struct: ZBase
        :returns: None
        :type return: None
        """
        self.get_map(z_struct)
        if self.smap:
            coord = world_from_pixel(self.smap, z_struct, z_struct.x, z_struct.y)
            self._y = coord.spherical.lat.arcsec
        else:
            try:
                v = Visual_File.get(Visual_File.id == self.visual_id)
                coord = v.world_from_pixel(z_struct.x, z_struct.y)
                self._y = coord.spherical.lat.arcsec
            except Exception as e:
                print(e)

    @property
    def xy(self):
        """
        Simultaneously set :attr:`x` and :attr:`y`.
        """
        return (self._x, self._y)

    @xy.setter
    def xy(self, z_struct):
        """Setter for x and y coordinates simultaneously
        
        :param z_struct: Zooniverse import structure
        :type z_struct: ZBase
        :returns: None
        :type return: None
        """
        self.get_map(z_struct)
        if self.smap:
            coord = world_from_pixel(self.smap, z_struct, z_struct.x, z_struct.y)
            self._x, self._y = coord.spherical.lon.arcsec, coord.spherical.lat.arcsec
        else:
            try:
                self._x, self._y = (
                    coord.spherical.lon.arcsec,
                    coord.spherical.lat.arcsec,
                )
                v = Visual_File.get(Visual_File.id == self.visual_id)
                coord = v.world_from_pixel(z_struct.x, z_struct.y)
            except Exception as e:
                print(e)

    @property
    def imageData(self):
        """
        The data associated with the zooniverse image from which this spatial classification was derived.
        """
        return (
            self.width,
            self.height,
            self.im_ll_x,
            self.im_ll_y,
            self.im_ur_x,
            self.im_ur_y,
        )

    @imageData.setter
    def imageData(self, zstruct):
        self.width = zstruct.width
        self.height = zstruct.height
        self.im_ll_x = zstruct.im_ll_x
        self.im_ll_y = zstruct.im_ll_y
        self.im_ur_x = zstruct.im_ur_x
        self.im_ur_y = zstruct.im_ur_y

    @classmethod
    def base_make(cls, z_struct):
        """Base function for creating Space_Obj
        
        :param z_struct: Zooniverse Structure
        :type z_struct: :class:`solar.zooniverse.structs.ZBase`
        :returns: Appropriate Space_Obj subclass
        :type return: Space_Obj
        """
        new = cls(
            subject_id=z_struct.subject_id,
            user_id=z_struct.user_id,
            workflow_id=z_struct.workflow_id,
            class_id=z_struct.class_id,
            fits_id=z_struct.fits_id,
            visual_id=z_struct.visual_id,
            frame=z_struct.frame,
        )
        new.imageData = z_struct
        new.smap = z_struct.fits_dict
        new.time = z_struct
        new.xy = z_struct
        return new

    @property
    def pixel_coords(self):
        """
        Convert the spatial coordinates of this object to coordinates on the image using the data :meth:`imageData`.
        """
        return pixel_from_world(
            self.smap, self.imageData, self.x, self.y, normalized=True
        )


@dataclass
class Space_Point(Space_Obj):
    def make_data(self):
        return (self.x, self.y, __since_start(self.time))

    @classmethod
    def make(cls, z_struct):
        return super().base_make(z_struct)


@dataclass
class Space_Rect(Space_Obj):
    #: The width of the rect in arcseconds
    w: float = -1
    #: The height of the rect in arcseconds
    h: float = -1
    #: The angle of the rect relative to the x axis
    a: float = -1

    def __str__(self):
        return super().__str__().format(f"{__r(self.w),__r(self.h)}")

    def make_data(self):
        return (self.x, self.y, self.w, self.h, self.a, __since_start(self.time))

    @classmethod
    def make(cls, z_struct):
        new = super().base_make(z_struct)
        new.w, new.h, new.a = z_struct.w, z_struct.h, z_struct.a
        return new



