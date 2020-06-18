from solar.database import *
from solar.database.tables.base_models import Base_Model


class Base_Service:

    base_api_url = None

    @staticmethod
    def _from_model(serv_obj):
        pass

    @property
    def data(self):
        return self._data

    def submit_request(self):
        # This method should submit the request for processing
        pass

    def fetch_data(self):
        # This method should return the data from the request
        pass

    def save_data(self):
        pass

    def save_request(self):
        pass

    def _verify_request(self):
        pass

    def __parse_attributes(self, attribute_list):
        pass
