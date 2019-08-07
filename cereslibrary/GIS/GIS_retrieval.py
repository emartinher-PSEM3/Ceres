#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 09:15:46 2018

@author: emh
"""

#Ceres_Filtration_v1.
#
#Tool for selection of nutrients recovery technologies.
#
#Edgar Martín Hernández.
#
#Cincinnati 2019.


# ===============================================================================================================================================================================================================================
# ###############################################################################################################################################################################################################################
# ===============================================================================================================================================================================================================================


def GIS_retrieval_module(latitude, longitude):
    
    import os
    import conda
    import pandas as pd
    import numpy as np
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
    
    input_point = np.array([float(latitude), float(longitude)]) 
    
    #input_point = np.array([39.014908, -98.010465])
    
    input_point_df = pd.DataFrame(
        {'Name': ['CAFO1'],
         'Latitude': [input_point[0]],
         'Longitude': [input_point[1]]})
    
#    poly  = geopandas.GeoDataFrame.from_file('cereslibrary/GIS/watershed/huc8sum.shp')
    poly  = geopandas.GeoDataFrame.from_file('cereslibrary/GIS/watershed/huc8sum.shp')
    point = geopandas.GeoDataFrame(input_point_df, geometry=geopandas.points_from_xy(input_point_df.Longitude, input_point_df.Latitude))
    
    poly.crs = {'init' :'epsg:4326'}
    point.crs = {'init' :'epsg:4326'}
    
    pointInPolys = sjoin(point, poly, how='left')
    
    #HUC8ContPoint = float(pointInPolys['HUC_8'])
    HUC8ContPoint = pointInPolys['HUC_8'].values[0]
         
#    HUC8_NARS_NLA_FINAL_P  = geopandas.GeoDataFrame.from_file('HUC8_NARS_NLA_FINAL_P/HUC8_NARS_NLA_FINAL_P.shp')
#    HUC8_NARS_NLA_FINAL_N  = geopandas.GeoDataFrame.from_file('HUC8_NARS_NLA_FINAL_N/HUC8_NARS_NLA_FINAL_N.shp')
    HUC8_NARS_NLA_FINAL_P  = geopandas.GeoDataFrame.from_file('cereslibrary/GIS/HUC8_NARS_NLA_FINAL_P/HUC8_NARS_NLA_FINAL_P.shp')
    HUC8_NARS_NLA_FINAL_N  = geopandas.GeoDataFrame.from_file('cereslibrary/GIS/HUC8_NARS_NLA_FINAL_N/HUC8_NARS_NLA_FINAL_N.shp')
    
    HUC8_NARS_NLA_FINAL_P.crs = {'init' :'epsg:4326'}
    HUC8_NARS_NLA_FINAL_N.crs = {'init' :'epsg:4326'}
    
    
    # =============================================================================
    # GIS data retrieval
    # =============================================================================
    
    HUC8_NARS_NLA_FINAL_P_index = HUC8_NARS_NLA_FINAL_P.set_index('HUC_8', drop=False)
    HUC8_NARS_NLA_FINAL_N_index = HUC8_NARS_NLA_FINAL_N.set_index('HUC_8', drop=False)
    
    TP_GIS = HUC8_NARS_NLA_FINAL_P_index.loc[HUC8ContPoint, 'PTL']
    NH4_GIS = HUC8_NARS_NLA_FINAL_N_index.loc[HUC8ContPoint, 'NH4']

    return  {'HUC8ContPoint':HUC8ContPoint, 'TP_GIS':TP_GIS, 'NH4_GIS':NH4_GIS}


