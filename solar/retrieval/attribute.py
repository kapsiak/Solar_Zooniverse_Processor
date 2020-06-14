import datetime
from solar.common.config import Config


class Attribute:
    def __init__(self, name, value, query_name=None):
        self.query_name = query_name if query_name else name
        self.name = name
        self.value = value

    def get_value(self, **kwargs):
        if type(self.value) == list:
            return ",".join(self.value)
        elif isinstance(self.value, datetime.datetime):
            return self.value.strftime(
                kwargs.get("time_format", Config["time_format_hek"])
            )
        else:
            return self.value

    def __eq__(self, other):
        if type(other) is str:
            return self.name == other
        else:
            return (self.name, self.value) == (other.name, other.value)
