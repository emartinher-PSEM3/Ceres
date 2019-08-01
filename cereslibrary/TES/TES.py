 
import os
import conda
import pandas as pd
import numpy as np
import json
# from shapely.geometry import Polygon as Poly

pd.options.display.max_columns = 250

conda_file_dir = conda.__file__
conda_dir = conda_file_dir.split('lib')[0]
proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
os.environ["PROJ_LIB"] = proj_lib

import matplotlib.pyplot as plt
import matplotlib.cm
import matplotlib.colors as colors

import geopandas
from geopandas.tools import sjoin
import geoplot as gplt
import geoplot.crs as gcrs


HUC12  = geopandas.GeoDataFrame.from_file('HUC12/HUC12.shp')
HUC12.crs = {'init' :'epsg:4326'}

# For folium
HUC12_json = HUC12.to_crs(epsg='4326').to_json()
HUC12.to_file('HUC12.geojson', driver='GeoJSON')
