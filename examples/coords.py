import solar.common.mapproc as mp
from solar.database.tables.fits_file import Fits_File
from solar.visual.annot import Rect_Annot, Circle_Annot, Text_Point
from solar.visual.img import Basic_Image

x, y = 0.7, 0.3

f = Fits_File.get()
header = f.get_header_as_dict()

bim = Basic_Image("png")
bim.create(f.file_path)

coord = mp.world_from_pixel_value(header, bim, x, y)
coord = tuple((round(x, 2) for x in coord))
pixel = mp.pixel_from_world(header, bim, *coord, normalized=True)


tp = Text_Point(*(pixel), f"{coord}")
circ = Circle_Annot(x, y)

bim.add_annotation(circ, tp)

bim.create(f.file_path)
bim.save_visual(f, "examples/coord.png")
