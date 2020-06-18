from solar.database import *
from solar.database.tables.base_models import Base_Model


def build_from_existing(service, *args, **kwargs):
    if len(args) == 1 and isinstance(args[0], Base_Model) and not kwargs:
        req = arg[0]
        query = Service_Request.select().join(Service_Parameter)


class Base_Service:

    base_api_url = None

    def submit_request(self):
        # This method should submit the request for processing
        pass

    def fetch_data(self):
        # This method should return the data from the request
        pass

    @property
    def data(self):
        return self._data

    def __parse_attributes(self, attribute_list):
        pass

    def _verify_request(self):
        pass

    @staticmethod
    def _from_model(serv_obj):
        pass

