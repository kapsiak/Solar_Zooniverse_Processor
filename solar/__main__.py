from solar.database import *
from solar.retrieval.hek_requester import Hek_Request
from solar.retrieval.cutout_requester import Cutout_Request, multi_cutout
from solar.plotting.image_maker import Unframed_Image, Basic_Image
from tqdm import tqdm


h = Hek_Request("2010-06-01T00:00:00", "2010-06-30T00:00:00", event_types=["cj"])
h.request()
create_tables()
l = [Cutout_Request(x) for x in Solar_Event.select()]
l = multi_cutout(l)
print(l)
for x in l:
    x.as_fits()

basic_image = Basic_Image('png')
unframed = Unframed_Image('png')
Fits_File.update_table()

for x in tqdm(Fits_File.select(), total = Fits_File.select().count()):
    im = Image_File.create_new_image(x, basic_image, overwrite= True)
