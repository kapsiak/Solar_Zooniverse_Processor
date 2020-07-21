from dataclasses import dataclass
from astropy.coordinates import SkyCoord


@dataclass()
class ZBase:
    subject_id: int
    fits_id: int
    subject_frame: int
    user_id: int


@dataclass
class Space_Rect(ZBase):
    base_point: SkyCoord
    w: float
    h: float
    a: float


@dataclass
class ZRect(ZBase):
    x: float
    y: float
    w: float
    h: float
    a: float

    def to_space(self):
        pass
        


@dataclass
class SpacePoint(ZBase):
    base_point: SkyCoord


@dataclass
class ZPoint(ZBase):
    x: float
    y: float
