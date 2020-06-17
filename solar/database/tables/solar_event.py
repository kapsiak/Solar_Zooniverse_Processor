import peewee as pw
from solar.common.config import Config
from datetime import datetime
from .base_models import Base_Model
from typing import Any, Dict


class Solar_Event(Base_Model):

    event_id = pw.CharField(default="NA", unique=True)
    sol_standard = pw.CharField(default="NA")

    start_time = pw.DateTimeField(default=datetime.now)
    end_time = pw.DateTimeField(default=datetime.now)

    coord_unit = pw.CharField(default="NA")

    x_min = pw.FloatField(default=-1)
    y_min = pw.FloatField(default=-1)

    x_max = pw.FloatField(default=-1)
    y_max = pw.FloatField(default=-1)

    hpc_x = pw.FloatField(default=-1)
    hpc_y = pw.FloatField(default=-1)

    hgc_x = pw.FloatField(default=-1)
    hgc_y = pw.FloatField(default=-1)

    frm_identifier = pw.CharField(default="NA")

    search_frm_name = pw.CharField(default="NA")

    description = pw.CharField(default="NA")

    source = pw.CharField(default="HEK")

    @staticmethod
    def from_hek(h: Dict[str, Any], source: str) -> None:
        params = dict(
            event_id=h["SOL_standard"],
            sol_standard=h["SOL_standard"],
            start_time=datetime.strptime(
                h["event_starttime"], Config["time_format_hek"]
            ),
            end_time=datetime.strptime(h["event_endtime"], Config["time_format_hek"]),
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
        try:
            return Solar_Event.create(**params)
        except pw.IntegrityError:
            return Solar_Event.get(Solar_Event.event_id == params["sol_standard"])
        else:
            return None

    def __repr__(self) -> str:
        return f""" <Solar_Event: {self.event_id}>"""

    def __str__(self) -> str:
        return f""" 
sol         =  {self.sol_standard}
coord(hpc)  = {self.hpc_x,self.hpc_y}
rec (ll ,ur)= {self.x_min, self.y_min} -- {self.x_max,self.y_max}
            """

    def __eq__(self, other):
        return self.event_id == other.event_id
