import peewee as pw
from solar.database import database
from datetime import datetime




class BaseModel(pw.Model):
    class Meta:
        database = database


class Solar_Event(BaseModel):

    event_id = pw.CharField(default='NA',unique=True)
    sol_standard = pw.CharField(default='NA')

    start_time = pw.DateTimeField(default= datetime.now)
    end_time = pw.DateTimeField(default = datetime.now)

    coord_unit = pw.CharField(default='NA')

    x_min = pw.FloatField(default = -1) 
    y_min = pw.FloatField(default = -1) 

    x_max = pw.FloatField(default = -1) 
    y_max = pw.FloatField(default = -1) 

    hpc_x = pw.FloatField(default = -1)
    hpc_y = pw.FloatField(default = -1)

    hgc_x = pw.FloatField(default = -1)
    hgc_y = pw.FloatField(default = -1)

    source = pw.CharField(default = 'NA')

    frm_identifier = pw.CharField(default= 'NA')

    search_frm_name = pw.CharField(default= 'NA')


    description = pw.CharField(default='NA')

    def __repr__(self):
        return f""" {self.event_id}: {self.description}"""

class Fits_Image(BaseModel):

    event = pw.ForeignKeyField(Solar_Event, backref = 'fits_files')

    server_file_name = pw.CharField(default='NA')

    file_path = pw.CharField(default='NA')
    file_hash  = pw.CharField(default='NA')

    instrument = pw.CharField(default='NA')
    channel = pw.CharField(default='NA')

    ssw_cutout_id = pw.CharField(default='NA')

    image_time = pw.DateTimeField(default= datetime.now())

    reference_pixel_x = pw.FloatField(default = -1)
    reference_pixel_y = pw.FloatField(default = -1)

    pixel_size = pw.FloatField(default = -1)
    im_dim_x = pw.IntegerField(default = -1)
    im_dim_y = pw.IntegerField(default = -1)

    def __repr__(self):
        return f"""Fits: {self.file_path}"""


TABLES = [Solar_Event,Fits_Image]
