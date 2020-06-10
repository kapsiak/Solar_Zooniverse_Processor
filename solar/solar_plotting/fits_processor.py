import sunpy.map
import matplotlib.pyplot as plt


def get_data(filename):
    return sunpy.map.Map(filename)


