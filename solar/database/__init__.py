import peewee as pw
from solar.common.config import Config

database = pw.SqliteDatabase(Config["database_path"], pragmas={"foreign_keys": 1})
