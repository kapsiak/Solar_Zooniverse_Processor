import unittest
from solar.common.utils import checksum, into_number
from pathlib import Path
from collections import namedtuple
from unittest.mock import MagicMock, Mock


class TestChecksum(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_name(self):
        string_list = [
            "Lorem i",
            "psum dolor si",
            "t amet, consetetur sadi",
            "psci",
            "ng eli",
            "tr, sed di",
            "am nonumy ei",
            "rmod tempor i",
            "nvi",
            "dunt ut labore et dolore magna ali",
            "quyam erat, sed di",
            "am voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet cli",
            "ta kasd gubergren, no sea taki",
            "mata sanctus est Lorem i",
            "psum dolor si",
            "t amet.",
        ]

        check = [
            "353d27abd140ffbe9266667d50bda7a6",
            "138fe61f57346f16c3855966622d44ac",
            "d1a9950ef11c24d1126cf4a5401c3582",
            "d381518b975343b3f8ac13fd64b173ec",
            "e9f1414ae3677727d7ea00729cd64af7",
            "e723c9c8ae3998d001b1167bbacfeed7",
            "1756d82371c60760da95d07842179c88",
            "887e624c664f266fc544eac820e80787",
            "dab23b204e6a399cad07894e430e780f",
            "91d1d70ccd0d716657b7760a2cfb6de4",
            "be5efb56225671232969493ddd6a1284",
            "3e49dd236f2322daac186b7ef90f54c4",
            "1310ae1bc0a5ba9f8833a29a5c10678c",
            "0df67f5e6bdcad3c34da05712cf900e6",
            "138fe61f57346f16c3855966622d44ac",
            "2e2d50de6efe76c7ceea5144d3b25fce",
        ]

        for x, y in zip(string_list, check):
            self.assertEqual(checksum(x), y)

    def test_file_or_string(self):
        return None


class Test_Into_Number(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_strings(self):
        strings = [
            "Rsjx9p3sK8LOATMhobudb0c5ntocBJzZbvPjC2k4",
            "XTVA5ZigFzry6sUsuyJccSzDWwADkYo3li5wtY1i",
            "LFwhqK2tJfVxPmbqqmcZtxMLLO346UWXgZNnYE6b",
            "pAqvcdv0F8pv79yKFb0465RPybkPW3gYycYAIQtV",
            "pAqvcdv0F8pv79yKFb0465RPybkPW3gYycYAIQtV",
            "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
            "Daisied springs show us how pigs can be britishes. One cannot separate bronzes from timely edgers. The first cancelled crop is, in its own way, a ton. The first bivalve hardboard is, in its own way, an april.",
            "Extending this logic, a meter is a jennifer from the right perspective. What we don't know for sure is whether or not they were lost without the rascal bomber that composed their icicle. The zeitgeist contends that a profit of the apple is assumed to be a chordate peony.",
        ]
        for string in strings:
            self.assertEqual(into_number(string), string)

    def test_float(self):
        nums = {
            "123.1231": 123.1231,
            ".1231": 0.1231,
            ".844": 0.844,
            ".0000023": 0.0000023,
            "0.0123": 0.0123,
            "1123.1": 1123.1,
            "2133.3331": 2133.3331,
            "1231231.11231": 1231231.11231,
            "6546.4": 6546.4,
            "4566.": 4566.0,
            "14444444.00000": 14444444.00000,
        }

        for x, y in nums.items():
            self.assertEqual(into_number(x), y)

    def test_int(self):
        nums = {
            "123": 123,
            "123441": 123441,
            "1234411234": 1234411234,
            "1234111234121": 1234111234121,
            "92456943": 92456943,
            "000000": 000000,
            "34563": 34563,
            "34563": 34563,
            "5463000": 5463000,
        }

        for x, y in nums.items():
            self.assertEqual(into_number(x), y)
