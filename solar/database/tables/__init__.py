from .solar_event import Solar_Event
from .service_request import Service_Request, Service_Parameter
from .fits_file import Fits_File, Fits_Header_Elem
from .visual_file import Visual_File
from .join_vis_fit import Join_Visual_Fits


tables = [
    Solar_Event,
    Service_Parameter,
    Service_Request,
    Fits_File,
    Fits_Header_Elem,
    Visual_File,
    Join_Visual_Fits,
]
