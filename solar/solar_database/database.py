import sqlite3
import json
from solar.common.solar_event import Solar_Event
from solar.solar_database import database_name

solar_connection = None


def get_connection():
    global solar_connection
    if not solar_connection:
        solar_connection = sqlite3.connect(database_name)
    return solar_connection


def event_exists(connection, solar_event):
    sol = solar_event.sol
    is_present_already = connection.execute(
        "SELECT * FROM hek_events WHERE sol = ?", (sol,)
    )
    if is_present_already.fetchone():
        return True
    else:
        return False


def insert_solar_event(connection, sol_ev):
    if not event_exists(connection, sol_ev):
        try:
            connection.execute(
                """INSERT INTO 
                hek_events 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?) """,
                sol_ev,
            )
        except sqlite3.Error as e:
            print(f"Could not insert event: {e}")
            connection.rollback()
        else:
            connection.commit()


def get_event(connection, solar_id):
    data = connection.execute("SELECT * FROM hek_events WHERE sol = ?", (sol,))
    return Solar_Event._make(data.fetchone())

def get_all_events(connection):
    data = connection.execute("SELECT * FROM hek_events WHERE sol = ?", (sol,))
    events = [Solar_Event._make(x) for x in data.fetchall()]
    return events


def insert_all_events(connection, events):
    for event in events:
        insert_solar_event(connection, event)


def update_record(connection, event, field, value):
        try:
            connection.execute(
            f""" UPDATE hek_events
            SET {field} = ? 
            WHERE event_id = ?;
                """,
            (value, event.event_id))
        except sqlite3.Error as e:
            print(f"Could not update event {event.sol}: {e}")
            connection.rollback()
        else:
            connection.commit()

if __name__ == "__main__":
    conn = sqlite3.connect(database_name)
    conn.execute(SCHEMA)
    conn.close()
