from __future__ import annotations
from typing import Any
import datetime
from solar.common.config import Config


class Attribute:
    def __init__(self, name: str, value: Any, query_name=None) -> None:
        self.query_name = query_name if query_name else name
        self.name = name
        self.value = value

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
            return ",".join(self.value)
        elif isinstance(self.value, datetime.datetime):
            return self.value.strftime(
                kwargs.get("time_format", Config["time_format_hek"])
            )
        else:
            return self.value

    def __eq__(self, other: Attribute) -> bool:
        if type(other) is str:
            return self.name == other
        else:
            return (self.name, self.value) == (other.name, other.value)
