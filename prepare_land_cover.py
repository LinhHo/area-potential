"""
Land cover classification categories.
Original categories taken from GlobCover 2009 land cover.
From Troendle et al. (2019) https://github.com/timtroendle/possibility-for-electricity-autarky
"""

import pandas as pd
import numpy as np

GlobCover = {
    11: "POST_FLOODING",
    14: "RAINFED_CROPLANDS",
    20: "MOSAIC_CROPLAND",
    30: "MOSAIC_VEGETATION",
    40: "CLOSED_TO_OPEN_BROADLEAVED_FOREST",
    50: "CLOSED_BROADLEAVED_FOREST",
    60: "OPEN_BROADLEAVED_FOREST",
    70: "CLOSED_NEEDLELEAVED_FOREST",
    90: "OPEN_NEEDLELEAVED_FOREST",
    100: "CLOSED_TO_OPEN_MIXED_FOREST",
    110: "MOSAIC_FOREST",
    120: "MOSAIC_GRASSLAND",
    130: "CLOSED_TO_OPEN_SHRUBLAND",
    140: "CLOSED_TO_OPEN_HERBS",
    150: "SPARSE_VEGETATION",
    160: "CLOSED_TO_OPEN_REGULARLY_FLOODED_FOREST",  # doesn't exist in Europe
    170: "CLOSED_REGULARLY_FLOODED_FOREST",  # doesn't exist in Europe
    180: "CLOSED_TO_OPEN_REGULARLY_FLOODED_GRASSLAND",  # roughly 2.3% of land in Europe
    190: "ARTIFICAL_SURFACES_AND_URBAN_AREAS",
    200: "BARE_AREAS",
    210: "WATER_BODIES",
    220: "PERMANENT_SNOW",
    230: "NO_DATA",
}

CoverType = {
    "POST_FLOODING": "FARM",
    "RAINFED_CROPLANDS": "FARM",
    "MOSAIC_CROPLAND": "FARM",
    "MOSAIC_VEGETATION": "FARM",
    "CLOSED_TO_OPEN_BROADLEAVED_FOREST": "FOREST",
    "CLOSED_BROADLEAVED_FOREST": "FOREST",
    "OPEN_BROADLEAVED_FOREST": "FOREST",
    "CLOSED_NEEDLELEAVED_FOREST": "FOREST",
    "OPEN_NEEDLELEAVED_FOREST": "FOREST",
    "CLOSED_TO_OPEN_MIXED_FOREST": "FOREST",
    "MOSAIC_FOREST": "FOREST",
    "CLOSED_TO_OPEN_REGULARLY_FLOODED_FOREST": "FOREST",
    "CLOSED_REGULARLY_FLOODED_FOREST": "FOREST",
    "MOSAIC_GRASSLAND": "OTHER",  # vegetation
    "CLOSED_TO_OPEN_SHRUBLAND": "OTHER",  # vegetation
    "CLOSED_TO_OPEN_HERBS": "OTHER",  # vegetation
    "SPARSE_VEGETATION": "OTHER",  # vegetation
    "CLOSED_TO_OPEN_REGULARLY_FLOODED_GRASSLAND": "OTHER",  # vegetation
    "BARE_AREAS": "OTHER",
    "ARTIFICAL_SURFACES_AND_URBAN_AREAS": "URBAN",
    "WATER_BODIES": "WATER",
    "NO_DATA": "NO_DATA",
}

# Arbitrary numbers assigned to land cover types
# to define suitable renewable energy potential
CoverTypeCode = {
    "FARM": 5,
    "FOREST": 6,
    "OTHER": 7,
    "URBAN": 8,
    "WATER": 9,
    "OCEAN": 10,  # assume NaN not classified as land cover means ocean
}


def convert_GlobCover_to_CoverType(land_cover_array):
    for value in GlobCover.keys():
        if value in land_cover_array:
            land_cover_array = land_cover_array.where(
                land_cover_array != value,
                other=CoverTypeCode[CoverType[GlobCover[value]]],
                drop=False,
            )
    land_cover_array = land_cover_array.fillna(10)

    # # remove the no data values - problem int in GlobCover but float in land_cover_array !!!
    # land_cover_array = land_cover_array.where(
    #     land_cover_array, other=np.nan, drop=False
    # )
    return land_cover_array

