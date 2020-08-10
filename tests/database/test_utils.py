import unittest
import solar.database.utils as ut
from solar.database.tables.hek_event import Hek_Event
from solar.database.tables.visual_file import Visual_File
from pathlib import Path
from solar.common.config import Config


class TestDBFormat(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dict(self):
        blank_format = "{test1} {test2} {test3}"
        vals = {"test1": 20, "test2": "Hello", "test3": [1, 2, 3]}
        baseline = blank_format.format(**vals)
        new = ut.dbformat(blank_format, **vals)
        self.assertEqual(new, baseline)

    def test_singlerow(self):
        h = Hek_Event()
        h.x_min = 10
        h.description = "Hello"
        h.hpc_x = 1.2
        blank_format = "{x_min} {description} {hpc_x}"
        desired = "10 Hello 1.2"
        new = ut.dbformat(blank_format, h)
        self.assertEqual(new, desired)

    def test_multirow(self):
        h = Hek_Event()
        v = Visual_File()
        h.x_min = 10
        h.description = "Hello"
        h.hpc_x = 1.2
        v.visual_generator = "TEST1"
        v.description = "TEST2"
        v.im_ll_x = 1.2
        blank_format = (
            "{x_min} {description} {hpc_x} {visual_generator} {description} {im_ll_x}"
        )
        desired = "10 Hello 1.2 TEST1 Hello 1.2"
        new = ut.dbformat(blank_format, h, v)
        self.assertEqual(new, desired)


class Testdbroot(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_root(self):
        bases = ["hello", Path("new"), "x", ""]
        desired = [Path(Config.db_save) / x for x in bases]
        for x, y in zip(bases, desired):
            self.assertEqual(ut.dbroot(x), y)
