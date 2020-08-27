Quickstart
==========

Setting up the database
-----------------------

In order to have persistence, we must first create the database. This is done by using the function :py:func:`~solar.database.create_tables`.

.. code-block:: python

    import solar.database as db
    db.create_tables()

This will create a database in the current directory.


Getting Events From HEK
-----------------------

Once the database has been setup we can begin to search the hek database for potential events. The interface for the HEK api is provided by the class :py:class:`~solar.service.hek.Hek_Service`.

.. code-block:: python

    import solar.service.hek as hserv
    
    hek = hserv.Hek_Service(
        event_starttime="2015-10-01T00:00:00",
        event_endtime="2015-11-15T00:00:00",
        event_type=["cj"],
    )

    # Submit the request
    hek.submit_request()

    found_events = hek.fetch_data()

    # Save the found events to the database
    hek.save_data()


Getting Fits Files from the Cutout Service
-------------------------------------------

There are several ways to generate a new :py:class:`~solar.service.cutout.Cutout_Service`. One may use an existing request or create one from attributes. A list of all api attributes may be found at `SSW API <https://www.lmsal.com/solarsoft//ssw_service/ssw_service_track_fov_api.html>`_.


.. code-block:: python

    from solar.database import Hek_Event, Cutout_Service
    from solar.service.attribute import Attribute

    # From fresh attributes
    cutout = Cutout_Service(Attribute("param1", val1), Attribute("param2", val2))

    # From kwargs
    cutout = Cutout_Service(param1 = val1, param2 = val2)

    # from an hek event
    event =  Hek_Event.get()
    cutout = Cutout_Service._from_event(event)

    # from an existing request
    old_cutout_request = Service_Request.select().where(
                Service_Request.service_type='ssw'
            ).get()
    cutout = Cutout_Service._from_model(old_cutout_request)


Requests are submitted in the same manner as the hek service. 

.. code-block:: python

    cutout.submit_request()
    cutout.save_request()


Data (fits files) is fetched in a similar manner as well, and is stored in the table :class:`~solar.database.tables.fits_file.Fits_File`.

.. code-block:: python

    cutout.fetch_data()
    cutout.save_data()
    cutout.save_request()




        
    

    
    




    


    

 
    
    





