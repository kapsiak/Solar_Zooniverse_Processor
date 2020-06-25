from solar.database.tables.base_models import UnionCol
import unittest
from datetime import datetime
from solar.common.config import Config


class TestUnionCol(unittest.TestCase):

    """Test case docstr."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_int_conversion(self):
        ints = [1234, 40404, 123, 12331, 12311, 111000000, 4949494]
        testers = [UnionCol(_value=str(i), _field_type="int") for i in ints]
        for x, y in zip(ints, testers):
            self.assertEqual(x, y.value)

    def test_float_conversion(self):
        ints = [123.4, 0.40404, 1.23, 12.331, 1.2311, 111000.000, 4949494.0]
        testers = [UnionCol(_value=str(i), _field_type="float") for i in ints]
        for x, y in zip(ints, testers):
            self.assertEqual(x, y.value)

    def test_str_conversion(self):
        ints = [
            "asdfasdf",
            "9q345asjfasdf",
            "cvxbcnofgif",
            "a",
            "",
            """ 
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
""",
        ]
        testers = [UnionCol(_value=str(i), _field_type="str") for i in ints]
        for x, y in zip(ints, testers):
            self.assertEqual(x, y.value)

    def test_datetime_conversion(self):
        pass

    def test_list_conversion(self):
        lists = [
            [1, 2, 3, 4, 5, 6, 6, 7, 764, 4],
            [9349348348393939483],
            [3],
            [30000000012, 3, 123, 123, 12, 312, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]

        testers = [
            UnionCol(
                _value=",".join([str(x) for x in i]), _field_type="list", _subtype="int"
            )
            for i in lists
        ]
        for x, y in zip(lists, testers):
            self.assertEqual(x, y.value)

    def test_list_conversion_float(self):
        lists = [
            [1, 2, 3, 4, 5, 6.333, 6, 7, 76.4, 4],
            [9349348348393.939483],
            [0.3],
            [30000.000012, 3, 123, 123, 12, 312, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.1],
        ]

        testers = [
            UnionCol(
                _value=",".join([str(x) for x in i]),
                _field_type="list",
                _subtype="float",
            )
            for i in lists
        ]
        for x, y in zip(lists, testers):
            self.assertEqual(x, y.value)

    def test_value_insertion(self):
        data = [
            (123, "123", "int", None),
            (44.123, "44.123", "float", None),
            ([1, 2, 3, 4], "1,2,3,4", "list", "int"),
            (
                [1.1231, 0.11, 1111.1, 11112],
                "1.1231,0.11,1111.1,11112",
                "list",
                "float",
            ),
            ("hello", "hello", "str", None),
            ("123.11", "123.11", "float", None),
            ("94843", "94843", "int", None),
            ("[123,123,555]", "123,123,555", "list", "int"),
            ("[1.23,12.3,.555]", "1.23,12.3,0.555", "list", "float"),
        ]

        for real, ideal, type1, type2 in data:
            uc = UnionCol()
            uc.value = real
            self.assertEqual(uc._value, ideal)
            self.assertEqual(uc._field_type, type1)
            self.assertEqual(uc._subtype, type2)
