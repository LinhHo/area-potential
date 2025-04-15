"""
Main module to apply technical mask
return the area potential for each technology

Structure
===

 3. Prepare the variables to the format used in the technical mask
 The specific codes are in separate files named Prepare_....py (land_cover, slope, settlement, bathymetry)
 4. Apply the technical mask
 User can define the technology and the threshold for each technology in the technical_table

 Returns
 ===

 Author: Linh Ho (TPM, TU Delft, 2025-04-08)

"""

import glob
import pandas as pd
import numpy as np
import geopandas as gpd
import xarray as xr
import rioxarray as rxr
from rasterio.transform import from_bounds

from prepare_land_cover import CoverTypeCode


technical_table = pd.DataFrame(
    {
        "pv-rooftop": [["URBAN"], np.nan, True, np.nan],
        "pv-open-field": [["FARM", "OTHER"], 3, False, np.nan],
        "wind-onshore": [["FARM", "FOREST", "OTHER"], 20, False, np.nan],
        "wind-offshore": ["land_sea_mask", np.nan, np.nan, -50],
    },
    index=["land_cover_type", "max_slope", "is_settlement", "max_depth"],
).T
print("Applying technical mask based on the following table...\n", technical_table)


def get_CoverTypeCode(technology):
    land_cover_type = technical_table.loc[technology, "land_cover_type"]
    return [CoverTypeCode[key] for key in land_cover_type]


def technical_mask(raster_input):
    """
    Actual technical mask
    """
    results = xr.Dataset()

    for technology in technical_table.index:
        if technology != "wind-offshore":
            results[technology] = (
                raster_input["land_cover"].isin(get_CoverTypeCode(technology))
                # & (raster_input["slope"] <= technical_table.loc[technology, "max_slope"])
                & (
                    raster_input["settlement"]
                    == technical_table.loc[technology, "is_settlement"]
                )
            )
        if technology == "wind-offshore":
            results[technology] = raster_input["land_sea_mask"] == 1 & (
                raster_input["bathymetry"]
                >= technical_table.loc[technology, "max_depth"]
            )
        # Note: PV rooftop: if account for land cover is 'URBAN', then very little area is available for PV rooftop
        # need to check URBAN type in land cover classification.
        # Currently, only use settlement (built up surface > 1%) as the sole criteria
        if technology == "pv-rooftop":
            results[technology] = (
                raster_input["settlement"]
                == technical_table.loc[technology, "is_settlement"]
            )

    return results
