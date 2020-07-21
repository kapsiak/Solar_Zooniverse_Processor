from collections import namedtuple

ZRect = namedtuple("ZRect", "x y w h angle fits_id")
ZPoint = namedtuple("ZPoint", "x y fits_id")

SpaceRect = namedtuple("SpaceRect", "x y w h angle")
SpacePoint = namedtuple("SpacePoint", "x y")
