from solar.service.attribute import Attribute as Att
from solar.service.utils import build_from_defaults
import unittest


class TestBuildDefaults(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_Operation(self):
        defaults = [Att("param1", 30), Att("param2", "lorem")]
        new = [Att("param1", 100), Att("new", [1, 2, 3, 4])]

        tester = build_from_defaults(defaults, new)

        wanted = [Att("param2", "lorem"), Att("param1", 100), Att("new", [1, 2, 3, 4])]

        for x in wanted:
            self.assertIn(x, tester)
