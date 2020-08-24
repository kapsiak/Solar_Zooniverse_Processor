import unittest
from solar.database.tables.base_models import PathField, File_Model, Base_Model
from tests.utils import test_db
from pathlib import Path


class TestPathField(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_save(self):
        pathstrs = [
            "first",
            "fist/one.py",
            "other.txt",
            "~/another/",
            "~/another/anotherone/again.txt",
            "cool/coolfile",
        ]

        paths = [Path(x) for x in pathstrs]
        pf = PathField()
        for x, y in zip([pf.db_value(x) for x in paths], [str(p) for p in paths]):
            self.assertEqual(x, y)

    def test_extract(self):
        pathstrs = [
            "first",
            "fist/one.py",
            "other.txt",
            "~/another/",
            "~/another/anotherone/again.txt",
            "cool/coolfile",
        ]

        paths = [Path(x) for x in pathstrs]
        pf = PathField()
        for x, y in zip(
            [pf.python_value(p) for p in pathstrs], [Path(p) for p in pathstrs]
        ):
            self.assertEqual(x, y)


class TestFileModel(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_name(self):
        pass
