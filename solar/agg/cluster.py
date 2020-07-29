from sklearn.cluster import AffinityPropagation
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn import metrics
from sklearn.datasets import make_blobs


def aff_fit(data):
    """TODO: Docstring for fit_points.

    :param point_list: TODO
    :returns: TODO

    """
    af = AffinityPropagation(preference=-50).fit(data)
    cluster_centers_indices = af.cluster_centers_indices_
    return cluster_centers_indices


def mean_fit(data):
    bandwidth = estimate_bandwidth(data, quantile=0.2, n_samples=500)
    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(data)
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_
    return (labels, cluster_centers)
