import sunpy.map
import matplotlib.pyplot as plt


def get_data(filename):
    return sunpy.map.Map(filename)

data = get_data('fits/NO_EVENT_ID/ssw_cutout_20111130_093108_AIA_304_.fts')
fig,axes = plt.subplots()
for x in data.meta:
    print(f"{x} = {data.meta[x]}")

