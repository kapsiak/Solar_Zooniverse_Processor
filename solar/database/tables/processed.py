from solar.database.tables.solar_event import Solar_Event
from solar.database.tables.base_models import Base_Model
import peewee as pw


class Processed_Subject(Base_Model):

    solar_event = pw.ForeignKeyField(Solar_Event, backref="zoo_jet")

    event_time = pw.DateTime
