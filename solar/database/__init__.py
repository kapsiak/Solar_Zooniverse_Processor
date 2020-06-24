import solar.database.tables as tb
from .database import database as db


def create_tables():
    db.create_tables(tb.tables)
