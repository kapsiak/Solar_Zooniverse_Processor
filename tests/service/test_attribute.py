from solar.service.attribute import Attribute
from solar.database.tables.service_request import Service_Request, Service_Parameter
import unittest



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
        ("asdf", [1, 2, 3, 4])
        ]
    
        atts = [Attribute(*x) for x in pairs]

        for x,(y,z) in zip(atts,pairs):
            self.assertEqual(x.name, y)
            self.assertEqual(x.value, z)
        
    def test_to_model(self):
        pass


    def test_from_model(self):
        pass


        
