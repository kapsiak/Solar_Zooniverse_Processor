from solar.database.tables.hek_event import Hek_Event
from solar.database.tables.base_models import Base_Model
import peewee as pw


class Processed_Subject(Base_Model):

    hek_event = pw.ForeignKeyField(Hek_Event, backref="zoo_jet")

    event_time = pw.DateTime
