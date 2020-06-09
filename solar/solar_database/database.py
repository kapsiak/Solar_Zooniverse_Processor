import sqlite3
import json
from Solar.common.solar_event import Solar_Event







def event_exists(solar_event):
    sol = solar_dict.sol
    is_present_already = conn.execute("SELECT * FROM hek_events WHERE sol = ?",(sol,))
    if is_present_already.fetchone():
        return True
    else:
        return False

def insert_solar_event(connection, sol_ev):
    if not event_exists(solar_dict):
        sol = sol_ev.sol
        x_min = sol_ev.x_min
        x_max = sol_ev.x_max
        y_min = sol_ev.y_min
        y_max = sol_ev.y_max
        hgc_x = sol_ev.hgc_x
        hgc_y = sol_ev.hgc_y
        start_time = sol_ev.start_time
        end_time = sol_ev.end_time
        try:
            connection.execute(
                """INSERT INTO 
                hek_events(sol,start_time,end_time,x_min,x_max,y_min,y_max,hgc_x,hgc_y) 
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (sol, start_time, end_time, x_min, x_max, y_min, y_max, hgc_x, hgc_y),
            )
        except sqlite3.Error as e:
            print(f"Could not insert event: {e}")
            connection.rollback()
        else:
            connection.commit()



def insert_all_events(connection, events):
    for event in events:
        insert_solar_event(connection, event)


if __name__=='__main__':
    conn = sqlite3.connect(database_name)
    conn.execute(SCHEMA)
    conn.close()


