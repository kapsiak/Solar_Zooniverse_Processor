import peewee as pw
from solar.common.config import Config
from datetime import datetime
from .base_models import Base_Model, UnionCol
from typing import Any, Dict
from .solar_event import Solar_Event


class Service_Request(Base_Model):
    event = pw.ForeignKeyField(Solar_Event, backref="service_requests", null=True)
    service_type = pw.CharField()
    # Status should be one of
    #  - unsubmitted
    #  - submitted (but not complete)
    #  - completed (request has been completed)
    status = pw.CharField()
    job_id = pw.CharField(null=True)

    def __getitem__(self, key: str) -> Any:
        """
        Get an item. References the Service_Parameters table to get the value of a header key

        :param key: The header key
        :type key: str
        :return: The value associated with the key
        :rtype: Any
        """
        self.parameters.where(Fits_Header_Elem.key == key).get().value

    def get_param(self, param):
        self.parameters.where(Fits_Header_Elem.key == key).get()

    def get_params_as_dict(self) -> Dict[str, Any]:
        return {x.key: x.value for x in self.parameters}

    def __str__(self):
        return (
            f"<Service_Req id = {self.id} | event = {self.event}>\n"
            f"{self.service_type}: {self.status}\n"
        )


class Service_Parameter(UnionCol):
    service_request = pw.ForeignKeyField(Service_Request, backref="parameters")
    key = pw.CharField()
    desc = pw.CharField(null=True)

    def __str__(self):
        return (
            f"<Service_Param id = {self.id} -> {self.service_request}>\n"
            f"{self.key} = {self.val}\n"
            f"Desc: {self.desc}"
        )
