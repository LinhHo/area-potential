"""
Convert elevation to slope
Based on https://www.earthdatascience.org/tutorials/get-slope-aspect-from-digital-elevation-model/
Questions:
- In Tim's code, I couldn't find the code to convert GMTED (Global Multi-resolution Terrain Elevation Data) to slope.
- The values of maximum slope (5 for PV, 20 for wind onshore) in percentage (I opted for this) or degree?
"""
import richdem as rd

