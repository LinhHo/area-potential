"""
This module determines in a raster if a pixel is a settlement based on a threshold percentage.
Default 1% of the area of the pixel.
The area of the pixel is calculated based on from T.Troendle determine_pixel_areas (utils.py and technically_eligible_area.py)
It does not (yet) include rooftop_area and building_share
Questions:
-
== From https://human-settlement.emergency.copernicus.eu/ghs_buS2023.php
The spatial raster dataset depicts the distribution of built-up surfaces, expressed as number of square metres.
The data report about the total built-up surface and the built-up surface allocated to dominant non-residential (NRES) uses.
"""

import numpy as np
import math


def _area_of_pixel(pixel_size, center_lat):
    """Calculate km^2 area of a wgs84 square pixel.

    Adapted from: https://gis.stackexchange.com/a/127327/2397

    Parameters:
        pixel_size (float): length of side of pixel in degrees.
        center_lat (float): latitude of the center of the pixel. Note this
            value +/- half the `pixel-size` must not exceed 90/-90 degrees
            latitude or an invalid area will be calculated.

    Returns:
        Area of square pixel of side length `pixel_size` centered at
        `center_lat` in km^2.

    """
    a = 6378137  # meters
    b = 6356752.3142  # meters
    e = math.sqrt(1 - (b / a) ** 2)
    area_list = []
    for f in [center_lat + pixel_size / 2, center_lat - pixel_size / 2]:
        zm = 1 - e * math.sin(math.radians(f))
        zp = 1 + e * math.sin(math.radians(f))
        area_list.append(
            math.pi
            * b**2
            * (math.log(zp / zm) / (2 * e) + math.sin(math.radians(f)) / (zp * zm))
        )
    return pixel_size / 360.0 * (area_list[0] - area_list[1]) / 1e6


def determine_pixel_areas(raster_input, bounds, resolution):
    """Returns a raster in which the value corresponds to the area [km2] of the pixel.

    This assumes the data comprises square pixel in WGS84.

    Parameters:
        crs: the coordinate reference system of the data (must be WGS84)
        bounds: an object with attributes left/right/top/bottom given in degrees
        resolution: the scalar resolution (remember: square pixels) given in degrees
    """
    # the following is based on https://gis.stackexchange.com/a/288034/77760
    # and assumes the data to be in WGS84
    assert (
        raster_input.rio.crs.to_epsg() == 4326
    ), "masked_rasters does not have the projection EPSG:4326"
    # assert crs == rasterio.crs.CRS.from_epsg("4326") # WGS84
    minx, miny, maxx, maxy = bounds
    width = int((maxx - minx) / resolution)  # Number of pixels in x-direction
    height = int((maxy - miny) / resolution)  # Number of pixels in y-direction

    latitudes = np.linspace(
        start=maxy, stop=miny, num=height, endpoint=True, dtype=np.float64
    )
    varea_of_pixel = np.vectorize(lambda lat: _area_of_pixel(resolution, lat))
    pixel_area = varea_of_pixel(latitudes)  # vector
    return pixel_area.repeat(width).reshape(height, width).astype(np.float64)


def is_settlement(raster_input, bounds, resolution, threshold_percentage=1 / 100):
    """
    Determine if a pixel is a settlement based on a threshold percentage, default 1%.
    """
    # pixel area in km2, settlement area in m2
    real_threshold = (
        determine_pixel_areas(raster_input, bounds=bounds, resolution=resolution)
        * 1000
        * threshold_percentage
    )
    result_boolean = raster_input >= real_threshold
    return result_boolean
