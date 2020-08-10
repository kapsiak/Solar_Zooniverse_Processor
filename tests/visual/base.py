import unittest
from solar.visual.base_visual import Visual_Builder
from sunpy.data.sample import AIA_171_IMAGE
import sunpy


class TestBaseVisual(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_hash(self):
        v = Visual_Builder("png")
        aiamap = sunpy.map.Map(AIA_171_IMAGE)
        v.map = aiamap
        print(hash(v))
