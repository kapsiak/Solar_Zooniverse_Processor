import sqlite3 


database_name  = 'test.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS 
hek_events (
    event_id TEXT NOT NULL,
    sol TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    x_min    INTEGER,
    x_max    INTEGER,
    y_min    INTEGER,
    y_max    INTEGER,
    hgc_x REAL,
    hgc_y REAL,
    instrument TEXT,
    ssw_job_id TEXT
);
"""

print(f'Initializing database {database_name}')
conn = sqlite3.connect(database_name)
conn.execute(SCHEMA)
conn.close()
