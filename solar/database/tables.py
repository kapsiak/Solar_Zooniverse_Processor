import peewee as pw
from solar.database import database, file_name_format
import solar.database.string as dbs
from datetime import datetime
from solar.retrieval.downloads import multi_downloader
from pathlib import Path
from solar.common.utils import checksum



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




class Fits_File(BaseModel):

    event = pw.ForeignKeyField(Solar_Event, backref = 'fits_files')

    sol_standard = pw.CharField(default='NA')

    server_file_name = pw.CharField(default='NA')
    server_full_path = pw.CharField(default='NA')

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
    
    def __str__(self):
        return f""" 
Event (ID/SOL)  = {self.event} | {self.sol_standard}
Server_Path     = {self. server_full_path}
File_Path       = {self.file_path}
Hash            = {self.file_hash}
            """
    
    
    def correct_file_path(self):
        self.file_path = dbs.format_string(file_name_format, self, file_type='FITS')
        self.file_path = self.file_path.replace(':','-')
        self.save()

    @staticmethod
    def correct_path_database():
        for f in Fits_File.select():
            f.correct_file_path()

    def get_hash(self):
        try:
            self.file_hash = checksum(self.file_path)
        except IOError as e:
            print(f"Could not get hash: {e}")
            self.file_hash = 'NA'
        self.save()
        return self.file_hash

    def check_integrity(self):
        p = Path(self.file_path)
        if p.is_file():
            if checksum(self.file_path) == self.file_hash:
                return True
        return False  

    @staticmethod
    def update_database():
        bad_files = [x for x in Fits_File.select() if not x.check_integrity() ]
        needed = None
        with database:
            needed = {
                f.server_full_path: f.file_path for f in bad_files
            }
        print(f"Found {len(bad_files)} missing/corrupted files")
        multi_downloader(needed)
        for f in bad_files:
            f.get_hash()
        print(f"Update complete")





TABLES = [Solar_Event,Fits_File]
