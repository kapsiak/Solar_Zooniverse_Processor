from solar.service.attribute import Attribute
from solar.database.tables.service_request import Service_Request, Service_Parameter
import unittest
from tests.utils import test_db


class TestAttribute(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_creation(self):
        pairs = [
            ("width", 100),
            ("events", ["xy", "yz", "ef"]),
            ("string", "Hello"),
            ("asdf", [1, 2, 3, 4]),
        ]

        atts = [Attribute(*x) for x in pairs]

        for x, (y, z) in zip(atts, pairs):
            self.assertEqual(x.name, y)
            self.assertEqual(x.value, z)

    @test_db()
    def test_to_model(self):
        att = [
            Attribute("param1", 20),
            Attribute("param2", 20.1),
            Attribute("param3", "hello"),
            Attribute("param4", [12, 2, 3, 4]),
        ]

        models = [a.as_model() for a in att]

        for a, m in zip(att, models):
            self.assertEqual(a.value, m.value)
            self.assertEqual(a.name, m.key)

    @test_db()
    def test_from_model(self):
        att = [
            Attribute("param1", 20),
            Attribute("param2", 20.1),
            Attribute("param3", "hello"),
            Attribute("param4", [12, 2, 3, 4]),
            Attribute("param5", [1.1, 2.2, 3.0, 0.5]),
            Attribute("param6", ["h", "asdf", "xxxxxx"]),
        ]

        models = [a.as_model() for a in att]

        new_att = [Attribute.from_model(x) for x in models]

        for a, m in zip(new_att, models):
            self.assertEqual(a.value, m.value)
            self.assertEqual(a.name, m.key)
