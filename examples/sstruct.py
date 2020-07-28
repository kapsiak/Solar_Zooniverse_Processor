from solar.service.hek import Hek_Service
from solar.database.tables.hek_event import Hek_Event
from solar.service.cutout import Cutout_Service, multi_cutout
from solar.database.tables.fits_file import Fits_File
from solar.database.tables.visual_file import Visual_File
from solar.database.tables.join_vis_fit import Join_Visual_Fits
from solar.visual.img import Basic_Image
from solar.visual.vid import Basic_Video
from solar.database import create_tables
from solar.zooniverse.export import zooniverse_export, prepare_row, split
from solar.visual.annot import Rect_Annot, Circle_Annot, Annot
from solar.zooniverse.zimport import load_all
from solar.agg.structs import Space_Point, Space_Obj
from solar.agg.cluster import aff_fit, mean_fit
import numpy as np

annots = load_all("scripts/class.csv")

data = [Space_Obj.make(x) for x in annots if Space_Obj.make(x)]
d_arr = np.array([np.array(d.make_data()) for d in data if isinstance(d, Space_Point)])
clusters = mean_fit()
print()

to_draw = [x for x in [Annot.to_annot(x) for x in annots] if x]

for x in to_draw:
    print(x)
bim = Basic_Image("png")
bim.add_annotation(*to_draw)


f = Fits_File.get()
im = Visual_File.create_new_visual(f, bim)
im.export("scripts/")
