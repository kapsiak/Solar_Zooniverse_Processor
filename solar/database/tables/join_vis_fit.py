import solar.database.tables.visual_file as vf
import solar.database.tables.fits_file as ff
from .base_models import Base_Model
import peewee as pw
from solar.database.database import database as db


class Join_Visual_Fits(Base_Model):
    fits_file = pw.ForeignKeyField(ff.Fits_File, backref="visual_join")
    visual_file = pw.ForeignKeyField(vf.Visual_File, backref="fits_join")

    class Meta:
        database = db


#        indexes = ((("fits_file", "visual_file"), True),)
