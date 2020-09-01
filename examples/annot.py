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
import math


bim = Basic_Image("png")

rect = Rect_Annot(x=0.4, y=0.4, w=0.3, h=0.4, a=45, lw=2)
circ = Circle_Annot(x=0.8, y=0.8)
rect_center = Circle_Annot(x=0.4, y=0.4, color="blue")
text = Text_Point(0.5, 0.5, "Look at this")
bim.add_annotation(rect, circ, rect_center, text)
fits_database_id = 1
f = Fits_File.get(Fits_File.id == fits_database_id)
bim.create(f.file_path)
bim.save_visual(f, "examples/new.png")
