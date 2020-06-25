import unittest
from solar.common.config import Config


class TestConfig(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_path(self):
        self.assertEqual(Config.db_save, "files")

    def test_path2(self):
        self.assertEqual(Config["db_save"], "files")

    def test_layered(self):
        self.assertEqual(Config.time_format.hek, "%Y-%m-%dT%H:%M:%S")

    def test_bool(self):
        self.assertEqual(Config.chatty, True)
