import sqlite3
import json
from solar.common.solar_event import Solar_Event
from solar.solar_database import database_name
from functools import wraps
# solar_connection = None

def attempt_connection(database_function):
    @wraps(database_function)
    def new_function(conn, *args,**kwargs):
        with conn:
            try:
                return database_function(conn, *args,**kwargs)
            except sqlite3.Error as e:
                print(
                f"""Encountered error when accessing database: 
                    ----> {e}
                """
                )
                return None
    return new_function

def get_connection():
    """
    Get a connection to the database file defined in __init__.py

    :return:  A connection to the database

    """

    solar_connection = sqlite3.connect(database_name)
    return solar_connection

@attempt_connection
def event_exists(connection, solar_event):
    """
    Check if an event exists, in order to avoid inserting duplicate events

    :param connection: sqlite3 database connection 
    :type connection: sqlite3.Connection
    :param solar_event: solar event to be inserted
    :type solar_event: Solar_Event  
    
    :returns: True if an event with solar_event.event_id already exists in database, false otherwise
    """
    sol = solar_event.sol
    is_present_already = connection.execute(
        "SELECT * FROM hek_events WHERE sol = ?", (sol,)
    )
    if is_present_already.fetchone():
        return True
    else:
        return False


@attempt_connection
def insert_solar_event(connection, sol_ev):
    """
    Insert an event into the database

    :param connection: sqlite3 database connection 
    :type connection: sqlite3.Connection
    :param solar_ev: solar event to be inserted
    :type solar_ev: Solar_Event  

    :returns: None

    """
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


@attempt_connection
def get_event(connection, event_id):
    """
    Return an event given an event id

    :param connection: sqlite3 database connection 
    :type connection: sqlite3.Connection
    :param event_id: string
    :type event_id:  string
    
    
    :returns: Found event is exists or None
    """

    data = connection.execute(
        "SELECT * FROM hek_events WHERE event_id = ?", (event_id,)
    )
    ret = data.fetchone()
    if ret:
        return Solar_Event._make(ret)
    else:
        return None


@attempt_connection
def get_all_events(connection):
    """
    Get all the events currently stored in database

    :param connection: sqlite3 database connection 
    :type connection: sqlite3.Connection

    :returns: List of events
    """
    data = connection.execute("SELECT * FROM hek_events")
    events = [Solar_Event._make(x) for x in data.fetchall()]

    return events


@attempt_connection
def insert_all_events(connection, events):
    """
    Inset a list of events into the database

    :param connection: sqlite3 database connection 
    :type connection: sqlite3.Connection
    :param events: A list of events
    :type events: list(Solar_Event)

    :returns: None
    """
    for event in events:
        insert_solar_event(connection, event)


@attempt_connection
def update_record(connection, event, field, value):
    """
    Update an existing event in the database.

    :param connection: sqlite3 database connection 
    :type connection: sqlite3.Connection
    :param event: the event to update
    :type event: Solar_Event
    :param field: the field to update
    :type field: string
    :param value: the value to insert into the field
    :type value: any 

    :returns: None
    """
    connection.execute(
        f""" UPDATE hek_events
    SET {field} = ? 
    WHERE event_id = ?;
        """,
        (value, event.event_id),
    )


if __name__ == "__main__":
    conn = sqlite3.connect(database_name)
    conn.execute(SCHEMA)
    conn.close()
