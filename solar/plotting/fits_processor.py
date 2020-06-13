import sunpy.map as sm
import matplotlib.pyplot as plt
import matplotlib.colors as colors


def get_data(filename):
    return sunpy.map.Map(filename)


def make_basic_image(filename, save_file):
    m = sm.Map(filename)
    fig = plt.figure()
    m.plot()
    plt.colorbar()
    plt.savefig(save_file, dpi=300)


def make_unframed_image(filename, save_file):
    m = sm.Map(filename)
    x = m.meta["naxis1"]
    y = m.meta["naxis2"]
    larger = max(x, y)
    fig = plt.figure()
    fig.set_size_inches(x / larger * 3, y / larger * 3)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    fig.add_axes(ax)
    plt.set_cmap("hot")
    ax.imshow(m.data, aspect="equal")
    plt.savefig(save_file, dpi=300)


def make_pcolor_image(filename, save_file):
    m = sm.Map(filename)
    x = m.meta["naxis1"]
    y = m.meta["naxis2"]
    larger = max(x, y)
    fig = plt.figure()
    fig.set_size_inches(x / larger * 3, y / larger * 3)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    fig.add_axes(ax)
    plt.set_cmap("hot")
    ax.pcolor(m.data, aspect="equal")
    plt.savefig(save_file, dpi=300)
