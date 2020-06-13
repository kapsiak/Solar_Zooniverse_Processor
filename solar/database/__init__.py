import peewee as pw

database_name = "test.db"
database_storage_dir = "files"
file_name_format = "{file_type}/{sol_standard}/{server_file_name}"
database = pw.SqliteDatabase(database_name, pragmas={"foreign_keys": 1})
