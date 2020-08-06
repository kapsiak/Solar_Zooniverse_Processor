import solar.database.tables.visual_file as vf
import solar.database.tables.fits_file as ff
from .base_models import Base_Model
import peewee as pw
from solar.database.database import database as db


class Join_Visual_Fits(Base_Model):
    """
    This class is a many-to-many relationship between the fits_files and images/videos generated from them
    
    This is necessary in order to allow videos (generated from many files) to be stored alongside the images.

    In the future it may work out better to refractor videos into the their own class, in which case this may become different/unnecessary
    """

    fits_file = pw.ForeignKeyField(ff.Fits_File, backref="visual_join")
    visual_file = pw.ForeignKeyField(vf.Visual_File, backref="fits_join")

    class Meta:
        database = db


#        indexes = ((("fits_file", "visual_file"), True),)
