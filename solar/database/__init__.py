from .tables.fits_file import Fits_File, Fits_Header_Elem
from .tables.service_request import Service_Request, Service_Parameter
from .tables.solar_event import Solar_Event
from .tables.visual_file import Visual_File
from .tables.join_vis_fit import Join_Visual_Fits
from .database import database as db


def create_tables():
    db.create_tables(
        [
            Fits_File,
            Fits_Header_Elem,
            Visual_File,
            Join_Visual_Fits,
            Solar_Event,
            Service_Parameter,
            Service_Request,
        ]
    )
