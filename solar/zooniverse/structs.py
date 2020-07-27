from dataclasses import dataclass
from astropy.coordinates import SkyCoord
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


@dataclass
class ZBool(ZBase):
    val: bool = False


@dataclass
class ZSpatial(ZBase):
    x: float = -1
    y: float = -1

    def flip_y(self, y_pix):
        # self.y = int(float(y_pix)) - self.y
        return self


@dataclass
class ZRect(ZSpatial):
    w: float = -1
    h: float = -1
    a: float = -1


@dataclass
class ZPoint(ZSpatial):
    pass
