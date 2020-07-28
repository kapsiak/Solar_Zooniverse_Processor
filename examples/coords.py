from solar.database.tables.fits_file import Fits_File
from solar.database.tables.visual_file import Visual_File
from solar.visual.annot import Circle_Annot
from solar.visual.img import Basic_Image


x, y = 1500, 300


v = Visual_File.get()
print(f"{v.im_ll_x,v.im_ll_y}")
f = v.get_fits()[0].fits_file
print(v.world_from_pixel(v.im_ll_x, v.im_ll_y))
c1 = Circle_Annot(x, y)

lon, lat = v.world_from_pixel_value(x, y)
bim = Basic_Image("png")
bim.add_annotation(c1)
im = Visual_File.create_new_visual(f, bim)
im.export("scripts/test.png")


print(f"lon,lat = {lon},{lat}")
px, py = v.pixel_from_world(x, y)
print(f"px,py = {px},{py}")
