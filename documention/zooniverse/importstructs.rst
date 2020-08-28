Import Structures
=================
.. module:: solar.zooniverse.structs

The module :mod:`solar.zooniverse.structs` defines a number of data classes which hold information about individual classifications. When importing data from zooniverse, each point, answer, or draw rectangle is loaded as a separate subclass of :class:`ZBase`. These classes most importantly contain the information required to convert pixel information to spatial information.


.. autoclass:: ZBase
    :members:

|
|

.. autoclass:: ZBool
    :members:

|
|

.. autoclass:: ZSpatial
    :members:

|
|

.. autoclass:: ZRect
    :members:

|
|

.. autoclass:: ZPoint
    :members:

|
|
