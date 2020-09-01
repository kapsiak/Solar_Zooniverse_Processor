from solar.service.hek import Hek_Service
from solar.database.tables.hek_event import Hek_Event
from solar.service.cutout import Cutout_Service, multi_cutout
from solar.database.tables.fits_file import Fits_File
from solar.database.tables.visual_file import Visual_File
from solar.database.tables.join_vis_fit import Join_Visual_Fits
from solar.visual.img import Basic_Image
from solar.visual.vid import Basic_Video
from solar.database import create_tables
from solar.zooniverse.export import zooniverse_export,  split
from solar.zooniverse.zimport import load_all
from solar.zooniverse.structs import ZRect, ZPoint, ZSpatial
from solar.agg.structs import make
from solar.agg.cluster import hdb, mean_fit, aff_fit
from sklearn.datasets import make_blobs
import numpy as np
from solar.visual.annot import Annot, Rect_Annot, Circle_Annot
import seaborn as sns
from solar.agg.metrics import ud1, compute_dmatrix, build_metric
from solar.agg.average import average


f = (
    Fits_File.select()
    .where(Fits_File.server_file_name == "ssw_cutout_20100620_111702_aia_304_.fts")
    .get()
)

create_tables()

data = load_all("examples/class.csv")
data = [x for x in data if isinstance(x, ZSpatial)]

vals = [x.as_data() for x in data]

data = vals

vals = compute_dmatrix(vals, metric=build_metric(ud1))

labels = hdb(vals, metric="precomputed")


color_palette = sns.color_palette("deep", 8)
cluster_colors = [color_palette[x] if x >= 0 else (0.5, 0.5, 0.5) for x in labels]


annots = [Annot.to_annot(x, 
   # color=c, 
    ls="--") for x, c in zip(data, cluster_colors)]

for x in set((x for x in labels if x > -1)):
    print(x)
    av = average(x, labels, data, narrow="rect")
    avc = average(x, labels, data, narrow="point")
    if av is not None:
        print(av)
       # annots.append(Rect_Annot(*av, color=color_palette[x], lw=2))
       # annots.append(Circle_Annot(*avc, color=color_palette[x], r=20))

annots = [x for x in annots if x]

bim = Basic_Image("png")
bim.add_annotation(*annots)
bim.create(f.file_path)
bim.save_visual(f, "examples/test.png")
