import peewee as pw
from solar.database import database
from solar.database.tables import TABLES,Solar_Event

from datetime import datetime
from solar.common.time_format import TIME_FORMAT as TF

def create_tables():
    with database:
        database.create_tables(TABLES)


def create_solar_event(h,source):
    return Solar_Event(
            event_id = h['SOL_standard']
            , sol_standard = h['SOL_standard']
            , start_time = datetime.strptime(h['event_starttime'], TF)
            , end_time = datetime.strptime(h['event_endtime'], TF)
            , coord_unit = h['event_coordunit']
            , x_min = h['boundbox_c1ll']
            , x_max = h['boundbox_c1ur']
            , y_min = h['boundbox_c2ll']
            , y_max = h['boundbox_c2ur']
            , hgc_x = h['hgc_x']
            , hgx_y = h['hgc_y']
            , frm_identifier = h['frm_identifier']
            , search_frm_name = h['search_frm_name']
            , source = source
            )
