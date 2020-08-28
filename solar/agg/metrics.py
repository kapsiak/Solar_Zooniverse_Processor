"""
Below are a number of functions for dealing with metrics.

As a rule, the first two letters denote what is being compared
and the d1, d2, ..., are just labels for distance 1, ...

*TODO* : Need to make metrics accept :mod:`solar.agg.structs` instead of just tuples.

:r:  rectangle
:p: point
:u: universal

|
|
"""

import math
from solar.zooniverse.structs import ZRect
import numpy as np
import shapely.geometry
import shapely.affinity
from .rect import compute_overlap, contour
from shapely.ops import nearest_points
from shapely.geometry import Point, Polygon


def rrd1(r1, r2):
    """Function rrd1: Individual component metric.
    
    Treats the rectangles as vectors and computes the distance between them. Normalizes angle.
    
    :param r1: rectangle 1
    :type r1: Tuple with length >= 5
    """
    center_dist_x = r1[0] - r2[0]
    center_dist_y = r1[1] - r2[1]
    wdiff = r1[2] - r2[2]
    hdiff = r1[3] - r2[3]
    da = (math.cos(math.radians(r1[4])) - math.cos(math.radians(r2[4]))) / 10
    # da = (r1[4] - r2[4])/180
    return np.linalg.norm([center_dist_x, center_dist_y, wdiff, hdiff, da])


def rrd2(r1, r2):
    """Function rrd2: 

    Computes the "distance" between rectangle by computing the ratio of the area of the overlap
    to the total area of the rectangle

    """
    return compute_overlap(r1, r2)


def rpd1(r1, p1):
    """Function rpd1: 

    Compares a point to rectangle by computing the distance between the point and the edge of a rectangle.
    This is done since rectangle are supposed to represent the extend of a jet, so reasonably the base of a jet
    should lie near the edge of the extend.
    
    """
    if len(r1) < len(p1):
        r1, p1 = p1, r1
    p1 = np.array(p1)
    dist_to_center = np.linalg.norm(np.array([r1[0], r1[1]]) - p1)

    if dist_to_center == 0:
        return 1
    # print(nearest_points(contour(r1),Point(*p1))[0].wkt)
    edist = np.linalg.norm(
        np.array(nearest_points(contour(r1).exterior, Point(*p1))[0]) - p1
    )
    if edist > 0:
        return edist
    else:
        return 0


def ppd1(p1, p2):
    """
    Compare two points as vectors.
    """
    return np.linalg.norm(np.array(p1) - np.array(p2))


def compute_dmatrix(val_list, metric=np.inner):
    """ 
    Compute the distance matrix for a set of features
    """
    return np.array([[metric(x, y) for x in val_list] for y in val_list])


def ud1(a, b, ppmet=ppd1, rrmet=rrd2, rpmet=rpd1):
    """
    Compare any combination of points and rectangles
    """
    if len(a) == 2 and len(b) == 2:
        return ppmet(a, b)
    if len(a) + len(b) == 7:
        return rpmet(a, b)
    if len(a) + len(b) == 10:
        return rrmet(a, b)
    return 0


def build_metric(func, *args, **kwargs):
    """ Construct a metric given some arguments    

    :param func: Metric
    :type func: func(a,b, args, kwargs)
    :param args: arguments to pass to metric
    :param kwargs: Kwargs to pass to metric
    :returns: A metric
    :type return: func(a,b)
    """

    def ret(a, b):
        return func(a, b, *args, **kwargs)

    return ret


if __name__ == "__main__":
    r = [1, 2, 3, 4, 45]
    p = [3, 5]
    p1 = rpd1(r, p)
