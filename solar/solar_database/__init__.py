import sqlite3 


database_name  = 'test.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS 
hek_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    sol TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    x_min    INTEGER,
    x_max    INTEGER,
    y_min    INTEGER,
    y_max    INTEGER,
    hgc_x REAL,
    hgc_y REAL
);
"""

conn = sqlite3.connect(database_name)
conn.execute(SCHEMA)
conn.close()
