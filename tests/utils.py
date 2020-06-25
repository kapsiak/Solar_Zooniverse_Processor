from functools import wraps
from peewee import SqliteDatabase
from solar.database.tables import tables
from solar.database.tables.solar_event import Solar_Event

table_tuple = tuple(tables)


def test_db(dbs: tuple = table_tuple):
    def decorator(func):
        @wraps(func)
        def test_db_closure(*args, **kwargs):
            test_db = SqliteDatabase(":memory:")
            with test_db.bind_ctx(dbs):
                test_db.create_tables(dbs)
                try:
                    func(*args, **kwargs)
                finally:
                    test_db.drop_tables(dbs)
                    test_db.close()

        return test_db_closure

    return decorator



