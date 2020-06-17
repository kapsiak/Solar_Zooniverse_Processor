from solar.database import *
from solar.database.tables.base_models import Base_Model
from solar.retrieval.attribute import Attribute, Attribute_List

class Request:
    """
    
    """
    @staticmethod
    def build_from_existing(service, *args , **kwargs):
        if len(args) ==1 and isinstance(args[0], Base_Model) and not kwargs:
            req = arg[0] 
            query = Service_Request.select().join(Service_Parameter).where(
                        
                    )
