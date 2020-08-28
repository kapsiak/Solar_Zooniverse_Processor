Space Data Classes
==================

Note that this portion of program still needs some work.


Spatial structures, as provided in the module :mod:`solar.agg.structs` encapsulate points and rectangles as they exist in real solar coordinates.
Specifically they contain the x and y hpc coordinate, possible the width and height of the rectangle, and the time (along with the entire relevant fits header and zooniverse image information).
With this information they are able to freely translate between coordinates in space and coordinates on a zooniverse image. 
This is potentially advantageous since it allows us to aggregate in actual space and time rather than in pixel/frame space. 

The majority of the time, these objects will be constructs from existing zooniverse classes in :mod:`solar.zooniverse.structs`.
This is done using the function :func:`solar.agg.structs.make`. In fact for almost most purposes this is the only function that will be really be necessary.


Spatial Data Classes
--------------------

.. automodule:: solar.agg.structs
    :members:
