import math
from solar.zooniverse.structs import ZRect
import numpy as np
import shapely.geometry
import shapely.affinity

def contour(r):
    w = r[2]
    h = r[3]
    c = shapely.geometry.box(-w / 2.0, -h / 2.0, w / 2.0, h / 2.0)
    rc = shapely.affinity.rotate(c, r[4])
    return shapely.affinity.translate(rc, r[0], r[1])


def get_area(r):
    return contour(r).area


def intersection(r1, r2):
    return contour(r1).intersection(contour(r2))


def i_area(r1, r2):
    total = get_area(r1) + get_area(r2)
    ia = intersection(r1, r2).area
    if ia > 0:
        return 1 / (2 * ia / total) - 1
    else:
        return np.inf


def compute_groups(rect_list):
    return


def normalize_angle(rect_list, angle_loc=4):
    """Function normalize_angle: Get rid of none instances and convert angles to better form
    
    :param rect_list: A list of rectangle data
    :type rect_list: List[List[len = 5]]
    :returns: The processed data
    """
    if isinstance(rect_list[0], ZRect):
        vals = [x.as_data() for x in rect_list if x]
    else:
        vals = rect_list
    for x in vals:
        print(x[angle_loc])
        x[angle_loc] = abs(math.cos(math.radians(x[angle_loc])))
    return vals


def compute_overlap(r1, r2):
    return i_area(r1, r2)
