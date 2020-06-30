import peewee as pw
from solar.common.config import Config

# Create the database
database = pw.SqliteDatabase(
    Config.db_path,
    pragmas={
        "journal_mode": "wal",
        "cache_size": -1 * 64000,  # 64MB
        "foreign_keys": 1,
        "ignore_check_constraints": 0,
        "synchronous": 0,
    },
)
