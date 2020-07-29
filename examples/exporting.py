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
from peewee import fn


to_export = [
    [
        y
        for y in Visual_File.select()
        .join(Join_Visual_Fits)
        .join(Fits_File)
        .join(Hek_Event)
        .where(Hek_Event.id == e)
        .order_by(Fits_File.image_time)
    ]
    for e in Hek_Event.select()
]

print(to_export)
to_export = [x[0:20] for x in to_export if x]

print([split(x, 4, 1) for x in to_export])
zooniverse_export(*[split(x, 4, 1) for x in to_export])
