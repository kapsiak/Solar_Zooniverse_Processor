import numpy as np


def narrowRect(x):
    return len(x) >= 5 or "rect" in x.__class__.__name__.lower()


def narrowPoint(x):
    return len(x) == 2 or "point" in x.__class__.__name__.lower()


def v_av(arr):
    return np.average(arr, axis=0)


def always(x):
    return True


narrowDict = {"rect": narrowRect, "point": narrowPoint}


def average(label, label_list, val_list, narrow=None, average=v_av):
    if narrow:
        narrow = narrowDict[narrow]
    else:
        narrow = always

    wanted = [y for x, y in zip(label_list, val_list) if x == label and narrow(y)]
    if not wanted:
        return None
    return average(wanted)


if __name__ == "__main__":
    x = [[1, 2], [1, 1, 2, 3, 4], [1, 5], [5, 1], [3, 3, 3, 3, 3], [3, 4], [-1, 2]]
    labels = [1, 1, 2, 1, 1, 2, 1]
    ret = average(1, labels, x, narrow="rect")
