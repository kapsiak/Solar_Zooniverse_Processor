import peewee as pw
from solar.database import database
from solar.database.tables import TABLES

def create_tables():
    with database:
        database.create_tables(TABLES)


