"""
Convert elevation to slope
Based on https://www.earthdatascience.org/tutorials/get-slope-aspect-from-digital-elevation-model/
Questions:
- In Tim's code, I couldn't find the code to convert GMTED (Global Multi-resolution Terrain Elevation Data) to slope.
- The values of maximum slope (5 for PV, 20 for wind onshore) in percentage (I opted for this) or degree?

Temporarily convert from EPSG 4326 to a UTM square metre projection, depending on the region,
for Vietnam it's UTM Zone 48N (EPSG:32648).
In the long-term, need to find a way to calculate globally independent of regions,
or find new dataset (Tim's code does not have any slope calculation, likely the data is already for slope)
"""

import numpy as np
import xarray as xr


def convert_elevation_to_slope(raster_input):
    # check if pixels are square
    print(raster_input.rio.resolution())

    # Reproject to a locally square in metre, depends on the regions
    elevation_utm = raster_input.rio.reproject("EPSG:32648")

    # Calculate pixel resolution
    res_x, res_y = elevation_utm.rio.resolution()
    res_x = abs(res_x)
    res_y = abs(res_y)
    print(res_x, res_y)

    # Calculate slope using numpy gradients
    dz_dx = elevation_utm.differentiate(coord="x") / res_x
    dz_dy = elevation_utm.differentiate(coord="y") / res_y
    slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
    slope_deg = np.degrees(slope_rad)

    # Wrap in xarray DataArray
    slope_da = xr.DataArray(
        slope_deg,
        coords=elevation_utm.coords,
        dims=elevation_utm.dims,
        attrs=elevation_utm.attrs,
    )
    slope_da.rio.to_raster("cropped_slope.tif")

    # # Reproject back to EPSG4326 to be compatible with the other datasets
    # slope_da = slope_da.rio.reproject_match()

    return slope_da
