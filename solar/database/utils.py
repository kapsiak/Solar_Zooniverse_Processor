import peewee as pw
from solar.database import database
from solar.database.tables import TABLES, Solar_Event, Fits_File
from pathlib import Path

from datetime import datetime
from solar.common.time_format import TIME_FORMAT as TF

import re


def create_tables():
    with database:
        database.create_tables(TABLES)


def initialize_save_folder():
    if not Path(database_storage_file).isdir():
        Path(database_storage_file).mkdir()
