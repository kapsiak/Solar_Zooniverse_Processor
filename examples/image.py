from solar.database.tables.fits_file import Fits_File
from solar.database.tables.visual_file import Visual_File
from solar.database.tables.join_vis_fit import Join_Visual_Fits
from solar.visual.annot import Circle_Annot, Rect_Annot
from solar.visual.img import Basic_Image
from sunpy.map import Map
from solar.common.mapproc import *
from math import sqrt, cos, sin, radians
from solar.database import create_tables

create_tables()


# bim = Basic_Image("png", dpi=1000)
#
# for f in Fits_File.select().where(
#        Fits_File.sol_standard == "SOL2010-07-27T00:00:31L090C081"
# ):
#    print(f.file_name)
#    print(f.sol_standard)
#    f.update_single()
#    im = Visual_File.create_new_visual(f, bim)
#    im.save()


v = (
    Visual_File.select()
    .join(Join_Visual_Fits)
    .join(Fits_File)
    .where(Fits_File.file_name == "ssw_cutout_20100921_215656_aia_304_.fts")
)

f = (
    Fits_File.select()
    .where(Fits_File.server_file_name == "ssw_cutout_20100620_111702_aia_304_.fts")
    .get()
)

print("Here")
f.update_single()

print(f)
