"""
 1. Crop and resample all input data to the same shape as variables in one rioxarray dataset
The shape can be provided by the user
the default is a rectangle with defined bounds in create_empty_geospatial_array
 2. Mask out protected area polygons
"""

import glob
import numpy as np
import xarray as xr
import rioxarray as rxr
import pandas as pd
import geopandas as gpd
from rasterio.transform import from_bounds


def create_empty_geospatial_array(bounds, resolution=30 / 3600, projection="EPSG:4326"):
    """
    Create an empty geospatial array with specified resolution, projection, and bounds.

    Args:
        bounds (tuple): Bounds of the array (minx, miny, maxx, maxy).
        resolution (float): Resolution of the array in degrees (default: 30 arc-seconds).
        projection (str): CRS of the array (default: "EPSG:4326").

    Returns:
        xarray.DataArray: An empty geospatial array.
    """
    # Calculate the number of pixels in x and y directions
    minx, miny, maxx, maxy = bounds
    width = int((maxx - minx) / resolution)  # Number of pixels in x-direction
    height = int((maxy - miny) / resolution)  # Number of pixels in y-direction

    # Create an empty numpy array filled with NaN
    data = np.full((height, width), np.nan, dtype=np.float32)

    # Define the transform (affine transformation) for the array
    transform = from_bounds(*bounds, width=width, height=height)

    # Generate longitude and latitude coordinates
    longitude = np.linspace(minx, maxx, width)  # Longitude values (x-coordinates)
    latitude = np.linspace(maxy, miny, height)  # Latitude values (y-coordinates)

    # Create an xarray.DataArray with the empty data and geospatial metadata
    geospatial_array = xr.DataArray(
        data,
        dims=("y", "x"),  # Define dimensions as y (latitude) and x (longitude)
        coords={
            "y": ("y", latitude, {"units": "degrees_north"}),  # Latitude coordinates
            "x": ("x", longitude, {"units": "degrees_east"}),  # Longitude coordinates
        },
    )

    # Assign CRS and transform to the DataArray
    geospatial_array.rio.write_crs(projection, inplace=True)  # Set the CRS
    geospatial_array.rio.write_transform(
        transform, inplace=True
    )  # Set the affine transform

    return geospatial_array


# Function to crop raster to defined geographic bounds
def get_same_shape_and_resolution(raster_input, reference_raster):
    """
    Resample and crop the raster_input
    to have the same bounds, projection, and resolution as the reference_raster
    """

    # Resamples the raster to a specified resolution and projection as the given sample
    resampled = raster_input.rio.reproject_match(reference_raster)

    # Crops the input raster to the specified geographic bounds
    # from the bounding box of the sample raster
    bounds = reference_raster.rio.bounds()
    cropped = resampled.rio.clip_box(*bounds)

    return cropped


# Function to mask out protected areas from raster
def mask_protected_areas(raster_input, path_protected_areas):
    """Masks out areas within protected regions defined in the vector file."""

    # Read the all shapefiles containing protected areas
    # www.protectedplanet.net/en contains multiple files
    try:
        files = glob.glob(path_protected_areas + "/*_shp_?/*_shp-polygons.shp")
        gdfs = (gpd.read_file(file) for file in files)  # generator
        protected_areas = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    except ValueError:
        files = glob.glob(path_protected_areas + "/*.shp")
        protected_areas = gpd.read_file(files[0])

    masked = raster_input.rio.clip(
        protected_areas.geometry, protected_areas.crs, invert=True
    )
    return masked


def process_all_rasters(path_input, bounds, resolution, path_protected_areas=None):
    """
    Process all rasters in the path_input dictionary and crop them to the specified bounds.
    """
    empty_array = create_empty_geospatial_array(bounds=bounds, resolution=resolution)

    processed_rasters = xr.Dataset()

    for var in path_input.keys():
        print(f"Processing variable: {var}")
        raster = rxr.open_rasterio(path_input[var], masked=True)
        _cropped_resampled_raster = get_same_shape_and_resolution(
            raster, empty_array
        ).sel(band=1)
        print(_cropped_resampled_raster.shape)

        processed_rasters[var] = xr.DataArray(
            data=_cropped_resampled_raster,
            dims=("y", "x"),
        )
    if path_protected_areas:
        processed_rasters = mask_protected_areas(
            processed_rasters, path_protected_areas
        )

    return processed_rasters


# if __name__ == "__main__":

#     # Example usage
#     bounds = (-180, -90, 180, 90)  # Global bounds
#     resolution = 30 / 3600  # 30 arc-seconds in degrees
#     projection = "EPSG:4326"  # by lat/lon, WGS84: by metre

#     empty_array = create_empty_geospatial_array(bounds, resolution, projection)
