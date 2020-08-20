import unittest
from solar.agg.average import average
import numpy as np


class TestAverage(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        self.data = [
            [1, 2],
            [1, 1, 2, 3, 4],
            [1, 5],
            [5, 1],
            [3, 3, 3, 3, 3],
            [3, 4],
            [-1, 2],
        ]
        self.labels = [1, 1, 2, 1, 1, 2, 1]

    def tearDown(self):
        pass

    def test_labelRect(self):
        x = average(1, self.labels, self.data, narrow="rect")
        wanted = np.array([2, 2, 2.5, 3, 3.5])
        self.assertTrue(np.allclose(x, wanted))

    def test_labelPoint(self):
        x = average(1, self.labels, self.data, narrow="point")
        wanted = np.array([1.66666667, 1.66666667])
        self.assertTrue(np.allclose(x, wanted))

    def test_customAverage(self):
        x = average(
            1,
            self.labels,
            self.data,
            narrow="rect",
            average=lambda v: np.array([1] * len(v[0])),
        )
        wanted = np.array([1, 1, 1, 1, 1])
        self.assertTrue(np.allclose(x, wanted), x)
