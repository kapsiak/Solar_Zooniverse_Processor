import unittest
from solar.agg.average import average


class TestAverage(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        self.data = [[1, 2], [1, 1, 2, 3, 4], [1, 5], [5, 1], [3, 3, 3, 3, 3], [3, 4], [-1, 2]]
        self.labels = [1, 1, 2, 1, 1, 2, 1]


    def tearDown(self):
        pass

    def test_labelRect(self):
        self.assertEqual(average(1,self.labels,self.data, narrow="rect", [)




        
        
