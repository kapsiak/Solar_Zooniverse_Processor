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
bi = Basic_Image("jpeg")

# files = Fits_File.select().where(Fits_File.event ==1)
# im = Visual_File.create_new_visual(files, vb)

f = Fits_File.get()
fs = Fits_File.select().where(Fits_File.event == 1)

test_image = Visual_File.create_new_visual(f, bi)
test_image.export("test/test.jpeg")
#
#test_vid = Visual_File.create_new_visual(fs, vb)
#test_vid.export("test/test.mp4")

def test(x,y):
    print(test_image.world_from_pixel(x,y))
