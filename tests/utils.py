from functools import wraps
from peewee import SqliteDatabase
from solar.database.tables import tables
import requests

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


def mock_get_json(param_resp_tuples):
    def mocked_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        found = [x for x in param_resp_tuples if x[0] == kwargs["params"]]
        if found:
            return MockResponse(found[0][1], 200)
        return MockResponse(None, 404)

    return mocked_requests_get
