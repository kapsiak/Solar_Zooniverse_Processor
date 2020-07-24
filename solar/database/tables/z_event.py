from .base_models import Base_Model
import peewee as pw
from .visual_file import Visual_File


class JoinVZ(Base_Model):
    visual_file = pw.ForeignKeyField(Visual_File, backref="vz_join")


class ZEvent(Base_Model):
    visual_file = pw.ForeignKeyField(Visual_File, backref="z_event")

    starttime = pw.DateTimeField()
    endtime = pw.DateTimeField()

    base_start_hpcx = pw.FloatField()
    base_start_hpcy = pw.FloatField()
    base_end_hpcx = pw.FloatField()
    base_end_hpcx = pw.FloatField()

    error_start_hpcx = pw.FloatField()
    error_start_hpcy = pw.FloatField()
    error_end_hpcx = pw.FloatField()
    error_end_hpcx = pw.FloatField()

    intersest = pw.FloatField()


JoinVZ.zevent = pw.ForeignKeyField(ZEvent, backref="vz_join")


class ZEventExtent(Base_Model):
    Z_Event = pw.ForeignKeyField(ZEvent)

    starttime = pw.DateTimeField()
    endtime = pw.DateTimeField()

    center_start_hpcx = pw.FloatField()
    center_start_hpcy = pw.FloatField()
    width = pw.FloatField()
    height = pw.FloatField()

    error_start_hpcx = pw.FloatField()
    error_start_hpcy = pw.FloatField()
    error_width = pw.FloatField()
    error_height = pw.FloatField()


class Classifications(Base_Model):
    zevent = pw.ForeignKeyField(ZEvent, backref="classif_ids")
    class_id = pw.IntegerField()
