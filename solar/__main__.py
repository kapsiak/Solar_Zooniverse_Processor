from solar.service import Hek_Service, Cutout_Service
from solar.database import *
from solar.visual.img import *
from solar.visual.vid import Video_Builder
import peewee as pw


create_tables()
#
# h = Hek_Service()
# for e in h.data:
#    try:
#        e.save()
#    except pw.IntegrityError:
#        pass
#

uf = Unframed_Image("jpeg")
vb = Video_Builder("mp4")
bi = Basic_Image("png")

#for x in Fits_File.select():
#    im = Visual_File.create_new_visual(x,bi)
#    im.save()

to_export = Visual_File.select().where(Visual_File.visual_type == 'png')
Visual_File.zooniverse_export(to_export)



