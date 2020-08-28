Project Structure
=================

This system has several functions:

- Interface with external services like HEK
- Store persistent information to avoid redundant calls to the services
- Generate visuals based on information acquired from these services
- Export visuals and data in a format compatible with Zooniverse_
- Import data from zooniverse as usable python objects
- Aggregate the imported data

Figure :numref:`figworkflow` shows a general representation of how this is accomplished.


.. _figworkflow:
.. figure:: /_static/workflow.png
  :alt: The general workflow

  The general workflow.

.. _Zooniverse: https://www.zooniverse.org/

The persistence is provided by an sqlite3 database. This database is accessed through the python wrapper `peewee <http://docs.peewee-orm.com/en/latest/>`_. An description of the api is provided in :doc:`/database/index`.
