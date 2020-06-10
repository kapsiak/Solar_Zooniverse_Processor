# Zooniverse Processor 

This is a package to aid in the construction of the JETS universe database. The primary sequence of operations envisioned for this package 

1. Download HEK Events (`solar.solar_retrieval.hek_requester`)
2. Store these events in a database 
3. Use the cutout service to pull these events (`solar.solar_retrieval.cutout_requester`)
4. Store job information in database 
5. Download appropriate fits files based on this data
6. Convert fits files into movies and pngs for use in zooniverse (`solar.solar_plotting.fits_processor`)

## Package Contents



