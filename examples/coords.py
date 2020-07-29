from solar.database.tables.fits_file import Fits_File
from solar.database.tables.visual_file import Visual_File
from solar.visual.annot import Circle_Annot, Rect_Annot
from solar.visual.img import Basic_Image
from sunpy.map import Map
from solar.common.mapproc import *


x, y = 500, 500

f = Fits_File.get()
c1 = Circle_Annot(0.5, 0.5)
r1 = Rect_Annot(0.4, 0.4, 0.2, 0.2, 45)
bim = Basic_Image("png")
bim.add_annotation(c1,r1)
bim.create(f.file_path)
bim.save_visual(f, "examples/test.png", clear_after=False)
# d = f.get_header_as_dict()
# m = Map(f.file_path)
#
#
# lon, lat = world_from_pixel_value(d, bim, x, y)
# px, py = pixel_from_world(m, bim, lon, lat)
#
# c2 = Circle_Annot(px, py)
# bim.draw_annotations()
# bim.save_visual(f, "examples/test.png")

# print(f"lon,lat = {lon}, {lat}")
# print(f"px,py = {px}, {py}")
