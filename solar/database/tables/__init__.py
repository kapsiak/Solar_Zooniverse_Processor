from .hek_event import Hek_Event
from .service_request import Service_Request, Service_Parameter, Service_Parameter_List
from .fits_file import Fits_File, Fits_Header_Elem, Fits_Header_Elem_List
from .visual_file import Visual_File
from .join_vis_fit import Join_Visual_Fits

# from .ucol import List_Storage


tables = [
    Hek_Event,
    Service_Parameter,
    Service_Parameter_List,
    Service_Request,
    Fits_File,
    Fits_Header_Elem,
    Fits_Header_Elem_List,
    Visual_File,
    Join_Visual_Fits,
]
