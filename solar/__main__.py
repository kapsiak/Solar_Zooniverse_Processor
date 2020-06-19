from solar.service import Hek_Service, Cutout_Service
from solar.database import *
from solar.visual.image_maker import *
import peewee as pw

create_tables()

h = Hek_Service()
for e in h.data:
    try:
        e.save()
    except pw.IntegrityError:
        pass

uf = Unframed_Image("png")
for x in Fits_File.select():
    im = Image_File.create_new_visual(x, uf)
