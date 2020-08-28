Processing Data
==========================

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    metrics
    aggregation
    spacestructs


At present, this program contains only rudimentary methods for aggregating and processing the classified data. 

The purpose of data aggregation is take the large number of different classifications made by zooniverse volunteers and attempt to extract a smaller amount of high quality data by doing some sort of "averaging." Of course, because of the complexity of the data, simply averaging is insufficient. Instead we use a number of *clustering algorithms*. These methods are described in :doc:`aggregation` and :doc:`metrics`. 


.. figure:: /_static/aggexample1.png    
    :alt: aggexample1

    Example of the result of data aggregation.

