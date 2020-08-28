Pixel to World Conversion
=========================


A key component of the program is the ability to translate between coordinates on a image (like a point clicked by a user) 
and an actual point in physics space. To complete this process, we need two pieces of information. 

The first is the WCS transformation which is provided to us by means of a fits header and sunpy's built in functions. These transformations allow us to translate between a pixel in the fits data to a world coordinate.

However, in general, out the fits data array will not occupy the entire image, and there may also be scaling issues. Therefore we also need information locating the actual data within the image. A diagram of this information is shown in :numref:`imagedia`.

.. _imagedia:
.. figure:: /_static/imageconv.png    
    :alt: imageconv

    Diagram showing how the image is described.


Translation Functions
---------------------

.. automodule:: solar.common.mapproc
    :members:
