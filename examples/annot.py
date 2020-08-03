from solar.database.tables.fits_file import Fits_File
from solar.database.tables.visual_file import Visual_File
from solar.visual.img import Basic_Image
from solar.database import create_tables
from solar.visual.annot import Rect_Annot, Circle_Annot, Annot, Text_Point
from solar.zooniverse.zimport import load_all
from solar.zooniverse.structs import ZPoint
from solar.agg.cluster import mean_fit
from itertools import cycle
import numpy as np
from solar.agg.structs import Space_Obj


bim = Basic_Image("png")
annots = load_all("examples/class.csv", row=1)

to_draw = [x for x in annots if isinstance(x, ZPoint)]
for s in to_draw:
    print(f"{s.x} , {s.y}")
fid = annots[0].fits_id
to_draw = [
    Text_Point(s.x, s.y, "{:.2f},{:.2f}".format(*Space_Obj.make(s).xy)) for s in to_draw
]
t = Text_Point(0.5, 0.5, "Hello World")
to_draw.append(t)

data = [Space_Obj.make(x) for x in annots]
bim.add_annotation(*to_draw)
f = Fits_File.get(Fits_File.id == fid)
im = Visual_File.create_new_visual(f, bim)
im.export("examples/new.png")
