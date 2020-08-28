import astropy.units as u
from sunpy.io.header import FileHeader
from sunpy.map import Map, GenericMap
import numpy as np
from astropy.wcs import WCS


def get_map(data):
    """Function get_map: Create a empty with the correct header
    
    :param data: TODO
    :type data: TODO
    :returns: TODO
    :type return: TODO
    """
    if issubclass(type(data), GenericMap):
        return data
    else:
        header_dict = FileHeader(data)
        fake_map = Map(np.zeros((1, 1)), header_dict)
        return fake_map


def pixel_from_world(sunmap, image_data, hpc_x, hpc_y, normalized=False):
    """Function pixel_from_world: Take a solar map, an image, and use these to convert a world coordinate to a coordinate in pixels on the image.
    If normalized is set to true, the resulting image coordinate is given in normalized image coordinates in the range [0,1].
    
    WARNING: This function is broken for now

    :param sunmap: The map containing the WCS data
    :type sunmap: sunpy.map.GenericMap
    :param image_data: The structure containing data about the image
    :type image_data: Visual_File or Subclass of Base_Visual
    :param hpc_x: x coordinate in space
    :type hpc_x: float
    :param hpc_y: y coordinate in space
    :type hpc_y: float
    :param normalized: If true, return normalized coordinates, defaults to False
    :type normalized: bool
    :returns: The resulting coordinates
    :type return: tuple(float)
    """

    if hasattr(image_data, "width"):
        im_width = image_data.width
        im_height = image_data.height
        im_ll_x = image_data.im_ll_x
        im_ll_y = image_data.im_ll_y
        im_ur_x = image_data.im_ur_x
        im_ur_y = image_data.im_ur_y
    elif len(image_data) == 6:
        im_width = image_data[0]
        im_height = image_data[1]
        im_ll_x = image_data[2]
        im_ll_y = image_data[3]
        im_ur_x = image_data[4]
        im_ur_y = image_data[5]
    else:
        raise ValueError

    sunmap = get_map(sunmap)
    wcs = sunmap.wcs
    fits_pixel_x, fits_pixel_y = wcs.wcs_world2pix(hpc_x / 3600, hpc_y / 3600, 1)

    fits_width, fits_height = wcs.pixel_shape

    x_norm, y_norm = fits_pixel_x / fits_width, fits_pixel_y / fits_height

    axis_x_normalized = im_ll_x + x_norm * (im_ur_x - im_ll_x)
    axis_y_normalized = im_ll_y + y_norm * (im_ur_y - im_ll_y)

    if normalized:
        return axis_x_normalized, axis_y_normalized
    else:
        return im_width * axis_x_normalized, im_height * axis_y_normalized


def world_from_pixel(sunmap, image_data, x, y):
    """Function world_from_pixel: Get a world pixel from a pixel coordinate.
    This is basically a wrapper the chooses the correct function based on the values of x and y

    :param sunmap: The map containing the WCS data
    :type sunmap: sunpy.map.GenericMap
    :param image_data: The structure containing data about the image
    :type image_data: Visual_File or Subclass of Base_Visual
    :param x: x coordinate in space
    :type x: float
    :param y: y coordinate in space
    :type y: float
    :returns: The resulting coordinates
    :type return: Sunpy coordinate object
    """
    if x > 1 and y > 1:
        return world_from_pixel_abs(sunmap, image_data, x, y)
    else:
        return world_from_pixel_norm(sunmap, image_data, x, y)


def world_from_pixel_value(sunmap, image_data, x, y):
    """Function world_from_pixel_value: 
    
    :param sunmap: The map containing the WCS data
    :type sunmap: sunpy.map.GenericMap
    :param image_data: The structure containing data about the image
    :type image_data: Visual_File or Subclass of Base_Visual
    :param x: x image coordinate
    :type x: float
    :pram y: y image coordinate
    :type y: float
    :returns: the heliorojectile coordinates cure sponging to the image coordinate
    :type return: tuple(float,float)
    """
    v = world_from_pixel(sunmap, image_data, x, y)
    return v.spherical.lon.arcsec, v.spherical.lat.arcsec


def world_from_pixel_abs(sunmap, image_data, x: int, y: int):
    """Function world_from_pixel_abs: Get a world pixel from a pixel coordinate.
    Here x and y are given in pixel coordinates with the origin being the bottom left

    :param sunmap: The map containing the WCS data
    :type sunmap: sunpy.map.GenericMap
    :param image_data: The structure containing data about the image
    :type image_data: Visual_File or Subclass of Base_Visual
    :param x: x image coordinate
    :type x: float
    :param y: y image coordinate
    :type y: float
    :returns: The resulting coordinates
    :type return: Sunpy coordinate object
    """
    im_width = image_data.width
    im_height = image_data.height
    return world_from_pixel_norm(sunmap, image_data, x / im_width, y / im_height)


def world_from_pixel_norm(sunmap, image_data, x: float, y: float):
    """Function world_from_pixel_norm: Get a world pixel from a pixel coordinate.
    Here x and y are given in normalized coordinates with the origin being the bottom left

    :param sunmap: The map containing the WCS data
    :type sunmap: sunpy.map.GenericMap
    :param image_data: The structure containing data about the image
    :type image_data: Visual_File or Subclass of Base_Visual
    :param x: x normalized image coordinate
    :type x: float
    :param y: y normalized image coordinate
    :type y: float
    :returns: The resulting coordinates
    :type return: Sunpy coordinate object
    """
    sunmap = get_map(sunmap)

    fits_width = sunmap.meta["naxis1"]
    fits_height = sunmap.meta["naxis2"]

    im_ll_x = image_data.im_ll_x
    im_ll_y = image_data.im_ll_y
    im_ur_x = image_data.im_ur_x
    im_ur_y = image_data.im_ur_y

    im_ur_y = im_ur_y
    im_ll_y = im_ll_y

    axis_x_normalized = (x - im_ll_x) / (im_ur_x - im_ll_x)
    axis_y_normalized = (y - im_ll_y) / (im_ur_y - im_ll_y)

    pix_x = axis_x_normalized * fits_width
    pix_y = (axis_y_normalized) * fits_height

    return sunmap.pixel_to_world(pix_x * u.pix, pix_y * u.pix)
