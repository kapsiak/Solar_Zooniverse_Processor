# Zooniverse Processor 

This is a package to aid in the construction of the JETS universe database. The primary sequence of operations envisioned for this package 

1. Download HEK Events (`solar.service.hek`)
2. Store these events in a database 
3. Use the cutout service to pull these events (`solar.service.cutout`)
4. Store job information in database 
5. Download appropriate fits files based on this data
6. Convert fits files into movies and pngs for use in zooniverse (`solar.solar_plotting.fits_processor`)

# Package Contents
## Request events from HEK
```python
from solar.service.hek import Hek_Service
h = Hek_Service('2010-06-01T00:00:00','2010-06-01T00:00:00',event_types=['cj'])
h.submit_request()
found_events = h.data
```

## Request a cutout

### Submit a request

```python
from solar.database import Solar_Event, Cutout_Service
event = Solar_Event.get()
cutout = Cutout_Service._from_event(event)
cutout.submit_request()
cutout.save_request()
```

Or from parameters

```python
cutout = Cutout_Service(Attributes)
```

Or from an existing request

```python
from solar.database import Service_Request
cutout = Cutout_Service._from_model(Service_Request.get())
```

The data can later be requested using 

```python
cutout.fetch_data()
found_fits_files = cutout.data
```

## Create Images

```python
from solar.visual.image_maker import Basic_Image
from solar.database import Fits_File, Image_File

fits = Fits_File.get()
im_maker = Basic_Image('png')
im = Image_File.create_new_image(fits,im_maker)
im.save()
```











