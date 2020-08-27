import peewee as pw
from .base_models import Base_Model
from .ucol import UnionCol, List_Storage
from typing import Any, Dict
from .hek_event import Hek_Event


class Service_Request(Base_Model):
    """
    Class to store information from both the hek and ssw requests, so thay they can be replicated later if needed.
    """
    
    #: Foreign key to the event from which this request was generated (used only for the ssw requests)
    event = pw.ForeignKeyField(Hek_Event, backref="service_requests", null=True)

    # The service type should be either hek or cutout.
    #: The type of service (either ssw or hek) 
    service_type = pw.CharField()

    #: Status should be one of
    #:  - unsubmitted
    #:  - submitted (but not complete)
    #:  - completed (request has been completed)
    status = pw.CharField()

    #: The job id of the request (used only for ssw)
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
        """Get a parameter of the request
        
        :param param: parameter name
        :type param: str
        :returns: the parameter, if it exists
        :type return: Service_Parameter
        """

        self.parameters.where(Service_Parameter.key == param).get()

    def get_params_as_dict(self):
        """ Get all the parameters as a dictionary
        :returns: Parameters formatted as dict
        :type return: dict
        """
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
