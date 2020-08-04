import solar.database.tables as tb
from .database import database as db


def create_tables():
    """Function create_tables: Create the tables for the database
    :returns: None
    :type return: None
    """
    db.create_tables(tb.tables)
