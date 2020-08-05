from solar.database import *
from solar.database.tables.base_models import Base_Model
from solar.common.printing import chat
from solar.database.tables.service_request import Service_Request
import peewee as pw


class Base_Service:
    """
    Base class for requests
    """

    base_api_url = None
    service_type = None

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
        self.__save_request_impl()

    def __save_request_impl(self):
        """Function __save_request_impl: Basic implementation for storing the service_request
        :returns: None
        :type return: None
        """
        if self.status == "unsubmitted":
            chat("No reason to save an unsubmitted service request")
            return None

        # First check if this request already has an id
        if not self.service_request_id:
            try:
                req = Service_Request.get(
                    Service_Request.job_id == self.job_id,
                    Service_Request.service_type == self.service_type,
                )
                chat(
                    (
                        "While saving this request, I found an existing request with a matching job id.\n"
                        "I am going to update that request instead"
                    )
                )
            except pw.DoesNotExist:
                chat(
                    ("I could not find any matching request. I am creating a new one.")
                )
                req = Service_Request.create(
                    service_type=self.service_type, status=self.status
                )
                chat(f"The new request's ID is {req.id}")
            except Exception as e:
                print(f"Other error: {e}")

        else:
            try:
                chat("This request already has an id, I will try saving it to that")
                req = Service_Request.get_by_id(self.service_request_id)
            except pw.DoesNotExist:
                print(
                    f"Somehow this request has an invalid id: {self.service_request_id}  "
                    "I don't know what to do with this so I am bailing."
                )
                return None

            except Exception as e:
                print(f"Other error: {e}")
                return None

        # One way or another, we now have a row in the datbase
        self.service_request_id = req.id

        # At this point we have a Service_Request object req, either from an existing request or one that we just created.
        # Now we add data to it

        # If this request has an event
        if hasattr(self, "event") and self.event:
            req.event = self.event
        else:
            req.event = None

        req.service_type = self.service_type
        req.status = self.status

        req.job_id = self.job_id

        # We also want to store the parameters of the request
        param_list = [p for p in req.parameters]
        my_params = [a.as_model(req) for a in self.params]

        new_list = []

        for param in my_params:
            search = [x for x in param_list if x.key == param.key]
            if not search:
                new_list.append(param)
            else:
                param.id = search[0].id
                new_list.append(param)

        req.save()
        for p in new_list:
            p.save()

    def _verify_request(self):
        pass

    def __parse_attributes(self, attribute_list):
        pass
