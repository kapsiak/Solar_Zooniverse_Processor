import peewee as pw
from solar.common.config import Config
from datetime import datetime
from .base_models import Base_Model
from typing import Any, Dict


class Hek_Event(Base_Model):
    """
    """

    #: Event_id is used mostly to circumvent issues where the sol standard contains ':'
    #: which on mac (BSD?) behaves like a directory delimiter and causes problems with file saving
    #: Event_id is Sol_Standard with the ':' replaced by '-'
    event_id = pw.CharField(default="NA", unique=True)

    #: The sol standard
    sol_standard = pw.CharField(default="NA")

    #: The event starttime
    start_time = pw.DateTimeField(default=datetime.now)
    #: the event endtime
    end_time = pw.DateTimeField(default=datetime.now)

    #: The unit the coordinates are given in
    coord_unit = pw.CharField(default="NA")

    #: the x coord of the lower left corner of the bounding box in hpc
    x_min = pw.FloatField(default=-1)
    #: the y coord of the lower left corner of the bounding box in hpc
    y_min = pw.FloatField(default=-1)

    #: the x coord of the upper right corner of the bounding box in hpc
    x_max = pw.FloatField(default=-1)
    #: the y coord of the upper right corner of the bounding box in hpc
    y_max = pw.FloatField(default=-1)

    #: The x coord of the event in HPC
    hpc_x = pw.FloatField(default=-1)
    #: The y coord of the event in HPC
    hpc_y = pw.FloatField(default=-1)

    #: The x coord of the event in HGC
    hgc_x = pw.FloatField(default=-1)
    #: The y coord of the event in HGC
    hgc_y = pw.FloatField(default=-1)

    #: Who identified the event
    frm_identifier = pw.CharField(default="NA")

    #: The algorithm that identified the event in HEK
    search_frm_name = pw.CharField(default="NA")

    #: An option description
    description = pw.CharField(default="NA")

    #: May never be used, just in case one day someone wants to add files from a different source
    source = pw.CharField(default="HEK")

    @staticmethod
    def from_hek(h, source):
        """Function from_hek: 

        Create a Hek event from a dict like object containing relevant parameters.
        Intended for use on the json returned by Hek_Service.
        
        :param h: The data structure containing the information
        :type h: dict-like
        :param source: Where the event came from
        :type source: str
        :returns: Hek_Event
        :type return: Hek_Event
        """
        params = dict(
            event_id=h["SOL_standard"].replace(":", "-"),
            sol_standard=h["SOL_standard"],
            start_time=datetime.strptime(h["event_starttime"], Config.time_format.hek),
            end_time=datetime.strptime(h["event_endtime"], Config.time_format.hek),
            coord_unit=h["event_coordunit"],
            x_min=h["boundbox_c1ll"],
            x_max=h["boundbox_c1ur"],
            y_min=h["boundbox_c2ll"],
            y_max=h["boundbox_c2ur"],
            hgc_x=h["hgc_x"],
            hgc_y=h["hgc_y"],
            hpc_x=h["hpc_x"],
            hpc_y=h["hpc_y"],
            frm_identifier=h["frm_identifier"],
            search_frm_name=h["search_frm_name"],
            description=h["event_description"],
            source=source,
        )
        return Hek_Event(**params)

    def __repr__(self) -> str:
        return f""" <Hek_Event: {self.event_id}>"""

    def __str__(self) -> str:
        return f"""
sol         =  {self.sol_standard}
coord(hpc)  = {self.hpc_x,self.hpc_y}
rec (ll ,ur)= {self.x_min, self.y_min} -- {self.x_max,self.y_max}
            """

    def __eq__(self, other):
        return self.event_id == other.event_id
