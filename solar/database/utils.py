import peewee as pw
from solar.database import database
from solar.database.tables import TABLES,Solar_Event,Fits_File
from pathlib import Path

from datetime import datetime
from solar.common.time_format import TIME_FORMAT as TF

import re



def create_tables():
    with database:
        database.create_tables(TABLES)

def create_solar_event(h,source='HEK'):
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
            , hgc_y = h['hgc_y']
            , hpc_x = h['hpc_x']
            , hpc_y = h['hpc_y']
            , frm_identifier = h['frm_identifier']
            , search_frm_name = h['search_frm_name']
            , source = source
            , description = h['event_description']
            )

def initialize_save_folder():
    if not Path(database_storage_file).isdir():
        Path(database_storage_file).mkdir()


def check_integrity(fits_file):
    p = Path(fits_file.file_path)
    if p.is_file():
        with open(p,'rb') as f:
            if hash(f.read()) == fits_file.file_hash:
                return True
    return False    






    
create_tables()
