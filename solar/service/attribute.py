from __future__ import annotations
from typing import Any
import datetime
from solar.common.config import Config
from solar.common.utils import into_number
from solar.database.tables.service_request import Service_Parameter


class Attribute:
    def __init__(self, name: str, value: Any = None) -> None:
        self.name = name
        self.value = value
        self.description = None

    def get_value(self, **kwargs) -> Any:
        """
        Get the value of the attribute. Several rules are implemented to determine the correct for of the value.
            - If value is a list, join list with commas
            - If value is a datetime.datetime, return a string formatted according to kwargs["time_format"] (defaults to Config["time_hek_format"]

        :param kwargs: time_format  
        :return: Appropriately formatted value
        :rtype: Any
        """
        if type(self.value) == list:
            return ",".join([str(x) for x in self.value])
        elif isinstance(self.value, datetime.datetime):
            return self.value.strftime(
                kwargs.get("time_format", Config.time_format.hek)
            )
        else:
            return str(self.value)

    def as_model(self, req=None):
        return Service_Parameter(
            service_request=req,
            key=self.name,
            val=self.get_value(),
            desc=self.description,
        )

    @staticmethod
    def from_model(tab):
        ret = Attribute(tab.key)
        if isinstance(ret, str):
            if "," in tab.val:
                temp = tab.value.split(",")
                ret.value = [into_number(x) for x in temp]
            else:
                ret.value = into_number(tab.value)
        else:
            ret.value = tab.val

        ret.description = tab.desc
        return ret

    def __eq__(self, other: Attribute) -> bool:
        if type(other) == str:
            return self.name == other
        else:
            return (self.name, self.value) == (other.name, other.value)

    def __hash__(self):
        return hash((self.name, (self.value)))

    def __str__(self):
        return (
            f"<Attribute>\n"
            f"{self.name} = {self.value} ~ {self.get_value()}\n"
            f"Desc: {self.description}"
        )


if __name__ == "__main__":
    print("Testing")
    from solar.database import create_tables

    create_tables()

    a = Attribute("width", 100)
    b = Attribute("events", ["xy", "yz", "ef"])
    c = Attribute("string", "Hello")
    d = Attribute("asdf", [1, 2, 3, 4])

    a = a.as_model()
    b = b.as_model()
    c = c.as_model()
    d = d.as_model()
    a = Attribute.from_model(a)
    b = Attribute.from_model(b)
    c = Attribute.from_model(c)
    d = Attribute.from_model(d)
    print(hash(a))
    print(hash(b))
    print(hash(c))
    print(hash(d))
