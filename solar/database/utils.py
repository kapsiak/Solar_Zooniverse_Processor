import peewee as pw
from solar.database import database
from solar.database.tables import TABLES, Solar_Event, Fits_File
from pathlib import Path

from datetime import datetime

import re
