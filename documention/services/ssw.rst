SSW Cutout Service
==================

.. module:: solar.service.cutout

The cutout service class is one of the more intensive in the package. 
Data is retrived in two stages. First, a request is submitted to the service using the :meth:`~Cutout.submit_request` function. It will then take some time for the SSW cutout service to process the request. At a later point, data is retrieved using the function  :meth:`~Cutout.fetch_data`. This data is stored in the :attr:`~Cutout.data` member, and can be saved automatically using the :meth:`~Cutout.save_data`. 

Not that is is *highly* advised to to save the request after both submission and data retrieval using the :meth:`~Cutout.save_request` method.


.. autoclass:: Cutout_Service
    :members:
    :private-members: _from_model, _from_event



