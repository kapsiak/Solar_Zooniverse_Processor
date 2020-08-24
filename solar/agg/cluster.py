from sklearn.cluster import AffinityPropagation
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn import metrics
from sklearn.datasets import make_blobs
import hdbscan


def aff_fit(data):
    """
    Perform an affinity propagation fit of the data

    For more information see `SKLearn MeanShift <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AffinityPropagation.html#sklearn.cluster.AffinityPropagation\>`

    :param data: data
    :type data: array type
    """
    af = AffinityPropagation(preference=-50).fit(data)
    cluster_centers_indices = af.cluster_centers_indices_
    return cluster_centers_indices


def mean_fit(data):
    """
    Perform a mean fit of the data.
    For more information see `SKLearn MeanShift <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.MeanShift.html#sklearn.cluster.MeanShift/>`

    :param data: data
    :type data: array type
    """
    bandwidth = estimate_bandwidth(data)
    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(data)
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_
    return (labels, cluster_centers)


def hdb(data, metric="euclidean"):
    clusterer = hdbscan.HDBSCAN(
        min_samples=2,
        alpha=1.0,
        # cluster_selection_epsilon=10.0,
        # min_cluster_size=2,
        metric=metric,
    )
    clusterer.fit(data)
    return clusterer.labels_
