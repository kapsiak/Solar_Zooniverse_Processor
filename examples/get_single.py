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

create_tables()

## Let us prepare a request for the hek service where we search for all coronal jets that occured between the October 1, 2015 and November 15, 2015.
#
# h = Hek_Service(
#    event_starttime="2010-06-01T00:00:00", event_endtime="2010-9-30T00:00:00"
# )
# h.submit_request()
# h.save_request()
# h.save_data()
## Now that request is prepared we can submit it.
#
## The list of events found by the search are stored in the data member variable
#
## To save the events to the database, we iterate over the events, and catch when we try to insert an even that already exists in the database
#
## Now let us get the fits files that correspond to these events
## Please see http://docs.peewee-orm.com/en/latest/peewee/api.html# for information on constructing queries.
# c = Cutout_Service._from_event(Hek_Event.get(3))
# c.submit_request()
# c.save_request()
# c.fetch_data()
# c.save_data()
#

bim = Basic_Image("png")

for x in Fits_File.select():
    im = Visual_File.create_new_visual(x, bim, overwrite=False)
    im.description = 'Test_Upload_1'
    if im:
        im.save()
