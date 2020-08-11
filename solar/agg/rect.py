import math
from solar.zooniverse.structs import ZRect
import numpy as np
import shapely.geometry
import shapely.affinity


class RotatedRect:
    def __init__(self, cx, cy, w, h, angle):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h
        self.angle = angle

    def get_contour(self):
        w = self.w
        h = self.h
        c = shapely.geometry.box(-w / 2.0, -h / 2.0, w / 2.0, h / 2.0)
        rc = shapely.affinity.rotate(c, self.angle)
        return shapely.affinity.translate(rc, self.cx, self.cy)

    def intersection(self, other):
        return self.get_contour().intersection(other.get_contour())

    @property
    def area(self):
        return self.get_contour().area

    def i_area(self, other):
        total = self.area + other.area
        ia = self.intersection(other).area
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


def compute_overlap():
    pass


def d1(r1, r2):
    center_dist_x = r1[0] - r2[0]
    center_dist_y = r1[1] - r2[1]
    wdiff = r1[2] - r2[2]
    hdiff = r1[3] - r2[3]
    da = (math.cos(math.radians(r1[4])) - math.cos(math.radians(r2[4]))) / 10
    # da = (r1[4] - r2[4])/180
    return np.linalg.norm([center_dist_x, center_dist_y, wdiff, hdiff, da])


def d2(r1, r2):
    r1 = RotatedRect(*r1)
    r2 = RotatedRect(*r2)
    return r1.i_area(r2)


def compute_dmatrix(rect_list, metric=np.inner):
    return np.array([[metric(x, y) for x in rect_list] for y in rect_list])


if __name__ == "__main__":
    v1 = np.asarray([[1, 2, 3, 1, 3], [1, 2, 3, 4, 5]])
    v2 = np.asarray([[3, 2, 1, 4], [2, 2, 3, 4]])
    v = np.array([[1, 2, 3, 4, 1]])
    w = np.array([[3, 2, 1, 4, 1]])
    print(compute_dmatrix(v1, d1))
