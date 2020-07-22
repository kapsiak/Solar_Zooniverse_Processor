import peewee as pw
from .base_models import Base_Model
from .ucol import UnionCol, List_Storage
from typing import Any, Dict
from .solar_event import Solar_Event


class Service_Request(Base_Model):
    event = pw.ForeignKeyField(Solar_Event, backref="service_requests", null=True)

    # The service type should be either hek or cutout.
    # TODO:  Add JSOC? #
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
        return self.parameters.where(Service_Parameter.key == key).get().value

    def get_param(self, param):
        self.parameters.where(Service_Parameter.key == key).get()

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
            f"------\n"
            f"<Service_Param id = {self.id} -> {self.service_request.id}>\n"
            f"{self.key} = {self.value}\n"
            f"Desc: {self.desc}"
        )


class Service_Parameter_List(List_Storage):
    table = pw.ForeignKeyField(Service_Parameter, backref="list_values")


Service_Parameter.list_storage_table = Service_Parameter_List
