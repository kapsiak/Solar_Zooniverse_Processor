from solar.database.tables.ucol import UnionCol, List_Storage
import unittest
from tests.utils import test_db
from datetime import datetime
from solar.common.config import Config


class TestUnionCol(unittest.TestCase):

    """Test case docstr."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_int_setter(self):
        ints = [1234, 40404, 123, 12331, 12311, 111000000, 4949494]
        testers = []
        for i in ints:
            u = UnionCol()
            u.value = i
            testers.append(u)
        for x, y in zip(ints, testers):
            self.assertEqual(x, y._value_int)
            self.assertIsNone(y._subtype)
            self.assertEqual("int", y._field_type)

    def test_int_getter(self):
        ints = [1234, 40404, 123, 12331, 12311, 111000000, 4949494]
        testers = []
        for i in ints:
            u = UnionCol()
            u._field_type = "int"
            u._subtype = None
            u._value_int = i
            testers.append(u)
        for x, y in zip(ints, testers):
            self.assertEqual(x, y.value)

    def test_float_setter(self):
        floats = [12.34, 0.40404, 1.23, 12.331, 1.2311, 1110.00000, 494949.4]
        testers = []
        for i in floats:
            u = UnionCol()
            u.value = i
            testers.append(u)
        for x, y in zip(floats, testers):
            self.assertEqual(x, y._value_float)
            self.assertIsNone(y._subtype)
            self.assertEqual("float", y._field_type)

    def test_float_getter(self):
        floats = [12.34, 404.04, 123.0, 123.31, 123.11, 1110.00000, 0.4949494]
        testers = []
        for i in floats:
            u = UnionCol()
            u._field_type = "float"
            u._subtype = None
            u._value_float = i
            testers.append(u)
        for x, y in zip(floats, testers):
            self.assertEqual(x, y.value)

    def test_string_setter(self):
        strings = ["", "aasd", "aasd  ", "asdf   asdf  a"]
        testers = []
        for i in strings:
            u = UnionCol()
            u.value = i
            testers.append(u)
        for x, y in zip(strings, testers):
            self.assertEqual(x, y._value_string)
            self.assertIsNone(y._subtype)
            self.assertEqual("str", y._field_type)

    def test_string_getter(self):
        strings = ["", "aasd", "aasd  ", "asdf   asdf  a"]
        testers = []
        for i in strings:
            u = UnionCol()
            u._field_type = "str"
            u._subtype = None
            u._value_string = i
            testers.append(u)
        for x, y in zip(strings, testers):
            self.assertEqual(x, y.value)

    def test_datetime_setter(self):
        datetimes = [
            datetime(1, 2, 12),
            datetime(1, 2, 3),
            datetime(12, 12, 12, microsecond=112311),
        ]
        testers = []
        for i in datetimes:
            u = UnionCol()
            u.value = i
            testers.append(u)
        for x, y in zip(datetimes, testers):
            self.assertEqual(x, y._value_datetime)
            self.assertIsNone(y._subtype)
            self.assertEqual("datetime", y._field_type)

    def test_datetime_getter(self):
        datetimes = [
            datetime(1, 2, 12),
            datetime(1, 2, 3),
            datetime(12, 12, 12, microsecond=112311),
        ]
        testers = []
        for i in datetimes:
            u = UnionCol()
            u._field_type = "datetime"
            u._subtype = None
            u._value_datetime = i
            testers.append(u)
        for x, y in zip(datetimes, testers):
            self.assertEqual(x, y.value)

    @test_db([UnionCol, List_Storage])
    def test_list_setter(self):
        UnionCol.list_storage_table = List_Storage
        data_lists = [[1, 3, 4], ["hello", "yes", "no"], [1.21, 121.11, 0.22]]
        testers = []
        for i in data_lists:
            u = UnionCol()
            u.value = i
            u.save()
            testers.append(u)
        for x, y in zip(data_lists, testers):
            self.assertEqual("list", y._field_type)
            self.assertEqual(str(type((x[0]))), y._subtype)
            self.assertEqual(x, [a.value for a in y.list_values])

    @test_db((UnionCol, List_Storage))
    def test_list_getter(self):
        UnionCol.list_storage_table = List_Storage
        data_lists = [[1, 3, 4], ["hello", "yes", "no"], [1.21, 121.11, 0.22]]
        testers = []
        for i in data_lists:
            u = UnionCol()
            u._field_type = "list"
            u._subtype = str(type((i[0])))
            u.value = i
            u.save()
            testers.append(u)
        for x, y in zip(data_lists, testers):
            self.assertEqual(x, y.value)
