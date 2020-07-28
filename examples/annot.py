from solar.database.tables.fits_file import Fits_File
from solar.database.tables.visual_file import Visual_File
from solar.visual.img import Basic_Image
from solar.database import create_tables
from solar.visual.annot import Rect_Annot, Circle_Annot, Annot
from solar.zooniverse.zimport import load_all
from solar.zooniverse.structs import ZPoint
from solar.agg.cluster import mean_fit
from itertools import cycle
import numpy as np


create_tables()
bim = Basic_Image("png")
annots = load_all("scripts/class.csv")
fid = annots[0].fits_id
annots = [Annot.to_annot(x) for x in annots if Annot.to_annot(x)]
bim.add_annotation(*annots)
f = Fits_File.get(fid)
im = Visual_File.create_new_visual(f, bim)
im.export("scripts/")
