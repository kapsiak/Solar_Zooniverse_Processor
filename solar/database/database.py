import peewee as pw
from solar.common.config import Config

database = pw.SqliteDatabase(
    Config["database_path"],
    pragmas={
        "journal_mode": "wal",
        "cache_size": -1 * 64000,  # 64MB
        "foreign_keys": 1,
        "ignore_check_constraints": 0,
        "synchronous": 0,
    },
)
