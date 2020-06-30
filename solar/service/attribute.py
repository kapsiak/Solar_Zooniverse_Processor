from __future__ import annotations
from typing import Any
import datetime
from solar.common.config import Config
from solar.common.utils import into_number
from solar.database.tables.service_request import Service_Parameter
from solar.common.convert import string_to_data, data_to_string


class Attribute:
    def __init__(self, name: str, value: Any = None, t_format = None) -> None:
        self.name = name
        self._value = value
        self._field_type = None
        self._sub_type = None
        self._format = t_format
        self.description = None

    @property
    def value(self, **kwargs) -> Any:
        """
        Get the value of the attribute. Several rules are implemented to determine the correct for of the value.
            - If value is a list, join list with commas
            - If value is a datetime.datetime, return a string formatted according to kwargs["time_format"] (defaults to Config["time_hek_format"]

        :param kwargs: time_format  
        :return: Appropriately formatted value
        :rtype: Any
        """
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    def f_value(self, val_form=None):
        if val_form:
            return val_form(self.value)
        else:
            return self.value

    def as_model(self, req=None):
        s = Service_Parameter(service_request=req, key=self.name, desc=self.description)
        print(f"Format is {self._format} for val {self._value}")
        s.format = self._format
        s.value = self._value
        return s

    @staticmethod
    def from_model(tab):
        ret = Attribute(tab.key)
        ret._format = tab.format
        ret._value = tab.value
        ret.description = tab.desc
        return ret

    def __eq__(self, other: Attribute) -> bool:
        if type(other) == str:
            return self.name == other
        else:
            return (self.name, self._value) == (other.name, other._value)

    def __str__(self):
        return (
            "<Attribute>\n" f"{self.name} = {self._value}\n" f"Desc: {self.description}"
        )


if __name__ == "__main__":
    print("Testing")
    from solar.database import create_tables

    create_tables()

    a = Attribute("width", 100)
    b = Attribute("events", ["xy", "yz", "ef"])
    c = Attribute("string", "Hello")
    d = Attribute("asdf", [1, 2, 3, 4])
    print("Initial ------------")
    print(a.value)
    print(b.value)
    print(c.value)
    print(d.value)
    a = a.as_model()
    b = b.as_model()
    c = c.as_model()
    d = d.as_model()
    print("As model ------------")
    print(f"{a.value} -> {a._value}")
    print(f"{b.value} -> {b._value}")
    print(f"{c.value} -> {c._value}")
    print(f"{d.value} -> {d._value}")
    a = Attribute.from_model(a)
    b = Attribute.from_model(b)
    c = Attribute.from_model(c)
    d = Attribute.from_model(d)
    print("As attribute ------------")
    print(a.value)
    print(b.value)
    print(c.value)
    print(d.value)
