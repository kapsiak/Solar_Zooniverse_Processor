from solar.service.hek import Hek_Service
from solar.service.cutout import Cutout_Service, multi_cutout
from solar.database.tables.fits_file import Fits_File
from solar.database.tables.visual_file import Visual_File
from solar.visual.img import Basic_Image
from solar.visual.vid import Basic_Video
from solar.database import create_tables

create_tables()


# Let us prepare a request for the hek service where we search for all coronal jets that occured between the October 1, 2015 and November 15, 2015.
hek = Hek_Service(
    event_starttime="2012-03-08T21:15:00",
    event_endtime="2012-03-08T22:15:00",
    event_type=["cj"],
)

# Now that request is prepared we can submit it.
hek.submit_request()

# The list of events found by the search are stored in the data member variable
hek.save_data()
events = hek.data
# To save the events to the database, we iterate over the events, and catch when we try to insert an even that already exists in the database

cutout_reqs = [Cutout_Service._from_event(event) for event in events]

# We use the helper function multi_cutout to make the requests asynchronously. The cutouts are saved
# Warning: this can take a very long time
completed_requests = multi_cutout(cutout_reqs)

for individual_req in completed_requests:
    individual_req.save_data()


# At this point we have a bunch of references to files in the SSW database.
# To actually download the files and extract header data, we need to update the Fits_File table

Fits_File.update_table()


# Lets make some pictures!
# Suppose we have an event with the solar id 'SOL123', and we want to create images for each fits file and a movie of the whole event.
# This can be done quickly


# This constructs two ``factory" functions
image_builder = Basic_Image("png")
video_builder = Basic_Video("mp4")

# fits_files = Fits_File.select().where(
#    Fits_File.sol_standard == "SOL2015-10-01T08:34:22L100C113"
# )
#
## First we iterate over all the files and create an image of each
# for fits in fits_files:
#    im = Visual_File.create_new_visual(fits, image_builder)
#    im.save()
#
#
## Then we string all the images together to create a video
# vid = Visual_File.create_new_visual(fits_files, video_builder)
