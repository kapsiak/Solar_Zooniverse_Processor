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
    for e in Hek_Event.select()[0:10]
]

to_export = [x for x in to_export if x]

zooniverse_export(*[split(x, 20, 2) for x in to_export])
