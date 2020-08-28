Annotations
===========

.. module:: solar.visual.annot


Annotations are extras that can be added to an image, as shown in :numref:`figannots` . 

Annotations are added to :class:`~solar.visual.base_visual.Visual_Builder` by means of the function :meth:`~solar.visual.base_visual.Visual_Builder.add_annotation`.

.. _figannots:
.. figure:: /_static/annots.png
  :alt: Examples of annotations


Annotation Types
----------------


.. autoclass:: solar.visual.annot.Annot
    :members:

|
|

.. autoclass:: solar.visual.annot.Rect_Annot
    :members:

|
|

.. autoclass:: solar.visual.annot.Circle_Annot
    :members:

|
|

.. autoclass:: solar.visual.annot.Text_Point
    :members:
