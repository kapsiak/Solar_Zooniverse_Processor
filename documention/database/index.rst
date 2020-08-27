Database Overview
=================

.. toctree::
    :maxdepth: 2
    :caption: Database:

    tables/hek
    tables/service
    tables/fits
    tables/visual

The heart of the persistence features of the program is an sqlite database. The database is accessed using the ORM package `peewee <http://docs.peewee-orm.com/en/latest/>`_ . Information about sqlite queries can be found in their documention.

The most important tables are described below:

:Hek Events: Events found from queries to the HEK database are stored in the table :class:`~solar.database.tables.hek_event.Hek_Event` 
:Service Request: Submitted service requests to hek or ssw (though is really only useful for hek) may be stored in the table :class:`~solar.database.tables.service_request.Service_Request`.
:Fits Files: Fits files found from queries to the SSW Cutout Service are stored in the table :class:`~solar.database.tables.fits_files.Fits_File`
:Generated Visuals: Images and videos generated from the Fits files are stores in the table :class:`~solar.database.tables.visual_file.Visual_File`

