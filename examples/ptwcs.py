import solar.common.mapproc as mp
import matplotlib.pyplot as plt
from solar.visual.img import Basic_Image

import sunpy.map
from sunpy.data.sample import AIA_171_IMAGE

aiamap = sunpy.map.Map(AIA_171_IMAGE)
print(type(aiamap))

bim = Basic_Image("png")

bim.create(aiamap, size=2)
bim.save_visual(None, "", fake_save=True, clear_after=False)

print(bim.im_ll_x, bim.im_ll_y)
x = mp.world_from_pixel(aiamap, bim, bim.im_ll_x, bim.im_ll_y)
x = mp.world_from_pixel(aiamap, bim, bim.im_ur_x, bim.im_ur_y)
y = mp.pixel_from_world(aiamap, bim, 1200, 1200, normalized=True)
print(y)
