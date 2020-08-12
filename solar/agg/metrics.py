import math
from solar.zooniverse.structs import ZRect
import numpy as np
import shapely.geometry
import shapely.affinity
from .rect import compute_overlap, contour
from shapely.ops import nearest_points
from shapely.geometry import Point, Polygon


def rrd1(r1, r2):
    center_dist_x = r1[0] - r2[0]
    center_dist_y = r1[1] - r2[1]
    wdiff = r1[2] - r2[2]
    hdiff = r1[3] - r2[3]
    da = (math.cos(math.radians(r1[4])) - math.cos(math.radians(r2[4]))) / 10
    # da = (r1[4] - r2[4])/180
    return np.linalg.norm([center_dist_x, center_dist_y, wdiff, hdiff, da])


def rrd2(r1, r2):
    return compute_overlap(r1, r2)


def rpd1(r1, p1):
    if len(r1) < len(p1):
        r1, p1 = p1, r1
    p1 = np.array(p1)
    dist_to_center = np.linalg.norm(np.array([r1[0], r1[1]]) - p1)

    if dist_to_center == 0:
        return 1
    # print(nearest_points(contour(r1),Point(*p1))[0].wkt)
    edist = np.linalg.norm(np.array(nearest_points(contour(r1).exterior, Point(*p1))[0]) - p1)
    print(edist)
    if edist > 0:
        return  edist
    else:
        return 0


def ppd1(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))


def compute_dmatrix(rect_list, metric=np.inner):
    return np.array([[metric(x, y) for x in rect_list] for y in rect_list])


def ud1(a, b, ppmet=ppd1, rrmet=rrd2, rpmet=rpd1):
    if len(a) == 2 and len(b) == 2:
        return ppmet(a, b)
    if len(a) + len(b) == 7:
        return rpmet(a, b)
    if len(a) + len(b) == 10:
        return rrmet(a, b)
    return 0


def build_metric(func, *args, **kwargs):
    def ret(a, b):
        return func(a, b, *args, **kwargs)

    return ret


if __name__ == "__main__":
    r = [1, 2, 3, 4, 45]
    p = [3, 5]
    p1 = rpd1(r, p)
    print(p1)
