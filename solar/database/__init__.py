import peewee as pw

database_name  = 'test.db'
database_storage_file = 'images'
file_name_format = '{sol_id}/{file_name}'

database = pw.SqliteDatabase(database_name)

