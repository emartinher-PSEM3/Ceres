#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 16:01:29 2019

@author: emh
"""

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

def PUptake(HUC8ContPoint, HUC6ContPoint):
#     input_point = np.array([float(latitude), float(longitude)]) 

#     #input_point = np.array([39.014908, -98.010465])

#     input_point_df = pd.DataFrame(
#         {'Name': ['CAFO1'],
#          'Latitude': [input_point[0]],
#          'Longitude': [input_point[1]]})

#     poly  = geopandas.GeoDataFrame.from_file('watershed/huc8sum.shp')
#     point = geopandas.GeoDataFrame(input_point_df, geometry=geopandas.points_from_xy(input_point_df.Longitude, input_point_df.Latitude))

#     poly.crs = {'init' :'epsg:4326'}
#     point.crs = {'init' :'epsg:4326'}

#     pointInPolys = sjoin(point, poly, how='left')

#     HUC8ContPoint = pointInPolys['HUC_8'].values[0]
    
#     LandCover_dfHUC8 = LandCover_dfHUC8.set_index('HUC_8')
    LandCover_Point = LandCover_dfHUC8.loc[HUC8ContPoint]
    AgriCensus_Point = AgriCensus_dfHUC6.loc[HUC6ContPoint]
    
    # P uptake forest
    Puptake_PFOR = 0.4535924*LandCover_Point['PFOR'].astype(float)/100 * ForestsPlantNutrientUptake.loc['P'].astype(float)/100 * ForestsPlantNutrientUptake.loc['PoundsAcre'].astype(float)
    # P uptake wetlands
    Puptake_PWETL = LandCover_Point['PWETL'].astype(float)/100 * Wetlands_Preg
    # P uptake croplands
    Puptake_PAGC= 0.4535924*LandCover_Point['PAGC'].astype(float)/100 * (AgriCensus_Point['Corn'].astype(float)/100 * 
                                             (PlantNutrientUptake_df.loc['Corn','P'].astype(float)/100 * PlantNutrientUptake_df.loc['Corn','PoundsAcre'].astype(float)+
                                             PlantNutrientUptake_df.loc['CornStraw','P'].astype(float)/100 * PlantNutrientUptake_df.loc['CornStraw','PoundsAcre'].astype(float))
                                             +
                                             AgriCensus_Point['Soybeans'].astype(float)/100 * 
                                             (PlantNutrientUptake_df.loc['Soybeans','P'].astype(float)/100 * PlantNutrientUptake_df.loc['Soybeans','PoundsAcre'].astype(float)+
                                             PlantNutrientUptake_df.loc['SoybeansStraw','P'].astype(float)/100 * PlantNutrientUptake_df.loc['SoybeansStraw','PoundsAcre'].astype(float))
                                             +
                                             AgriCensus_Point['Small grains'].astype(float)/100 * 
                                             (SmallGrainsPlantNutrientUptake.loc['P'].astype(float)/100 * SmallGrainsPlantNutrientUptake.loc['PoundsAcre'].astype(float))
                                             +
                                             AgriCensus_Point['Cotton'].astype(float)/100 * 
                                             (PlantNutrientUptake_df.loc['Cotton','P'].astype(float)/100 * PlantNutrientUptake_df.loc['Cotton','PoundsAcre'].astype(float)+
                                             PlantNutrientUptake_df.loc['CottonStraw','P'].astype(float)/100 * PlantNutrientUptake_df.loc['CottonStraw','PoundsAcre'].astype(float))
                                             +
                                             AgriCensus_Point['Rice'].astype(float)/100 * 
                                             (PlantNutrientUptake_df.loc['Rice','P'].astype(float)/100 * PlantNutrientUptake_df.loc['Rice','PoundsAcre'].astype(float)+
                                             PlantNutrientUptake_df.loc['RiceStraw','P'].astype(float)/100 * PlantNutrientUptake_df.loc['RiceStraw','PoundsAcre'].astype(float))
                                             +
                                             AgriCensus_Point['Vegetables'].astype(float)/100 * 
                                             (VegetablesPlantNutrientUptake.loc['P'].astype(float) * VegetablesPlantNutrientUptake.loc['PoundsAcre'].astype(float))
                                             +
                                             AgriCensus_Point['Orchards'].astype(float)/100 * 
                                             (PlantNutrientUptake_df.loc['Apples','P'].astype(float)/100 * PlantNutrientUptake_df.loc['Apples','PoundsAcre'].astype(float))
                                             +
                                             AgriCensus_Point['Greenhouse'].astype(float)/100 * 
                                             (VegetablesPlantNutrientUptake.loc['P'].astype(float)/100 * VegetablesPlantNutrientUptake.loc['PoundsAcre'].astype(float))
                                             +
                                             AgriCensus_Point['Other'].astype(float)/100 * 
                                             (OtherCropsPlantNutrientUptake.loc['P'].astype(float)/100 * OtherCropsPlantNutrientUptake.loc['PoundsAcre'].astype(float))
                                             )

    # P uptake pasture
    Puptake_PAGP = 0.4535924*LandCover_Point['PAGP'].astype(float)/100 * PasturePlantNutrientUptake.loc['P'].astype(float)/100 * PasturePlantNutrientUptake.loc['PoundsAcre'].astype(float)
    # P uptake development areas
    Puptake_PDEV = 0.4535924*LandCover_Point['PDEV'].astype(float)/100 * 0
    
    TotalHUC_PUptake = AreaHUC8.loc[HUC8ContPoint, 'AREA_ACRES'].astype(float)*(Puptake_PFOR+Puptake_PWETL+Puptake_PAGC+Puptake_PAGP+Puptake_PDEV)
    
#    TotalHUC_PUptake = TotalHUC_PUptake.to_numpy()
    TotalHUC_PUptake = TotalHUC_PUptake.item()
    TotalHUC_PUptake_totalHUCs.append(TotalHUC_PUptake)
    
    return TotalHUC_PUptake



LandCover_dfHUC8 = pd.read_csv('DatabasesClean/LandCover_HUC8_reconciliated.csv', converters={'HUC_8': lambda x: str(x), 'HUC_6': lambda x: str(x)})
LandCover_dfHUC8 = LandCover_dfHUC8.set_index('HUC_8')

AgriCensus_dfHUC6 = pd.read_csv('DatabasesClean/Agricensus_reconciliated.csv', converters={'HUC_6': lambda x: str(x)})
AgriCensus_dfHUC6 = AgriCensus_dfHUC6.set_index('HUC_6')
AgriCensus_dfHUC6 = AgriCensus_dfHUC6.fillna(0)

poly  = geopandas.GeoDataFrame.from_file('watershed/huc8sum.shp')
poly['HUC_8'] = poly['HUC_8'].astype(str)
AreaHUC8 = poly.set_index('HUC_8', drop=False)[['AREA_ACRES','HUC_8']]



# Import databases
PlantNutrientUptake_df = pd.read_csv('DatabasesClean/PlantNutrientUptake.csv', index_col='Crop')
ForestsPlantNutrientUptake = pd.read_csv('DatabasesClean/ForestsPlantNutrientUptake.csv', index_col='Item')
SmallGrainsPlantNutrientUptake = pd.read_csv('DatabasesClean/SmallGrainsPlantNutrientUptake.csv', index_col='Item')
VegetablesPlantNutrientUptake = pd.read_csv('DatabasesClean/Vegetables_GreenhousePlantNutrientUptake.csv', index_col='Item')
OtherCropsPlantNutrientUptake = pd.read_csv('DatabasesClean/OtherCropsPlantNutrientUptake.csv', index_col='Item')
PasturePlantNutrientUptake = pd.read_csv('DatabasesClean/PasturePlantNutrientUptake.csv', index_col='Item')

Wetlands_Preg = 0.77*1E-3/0.0002471052 #Kg/Acre

TotalHUC_PUptake_totalHUCs = []
counter_HUC8 = []

HUC_8_array =  AreaHUC8['HUC_8'].to_numpy()
HUC_8_array_iter = iter(HUC_8_array)
for HUC8 in HUC_8_array:
    HUC8ContPoint = HUC8
    HUC6ContPoint = HUC8ContPoint[:6]
    PUptake(HUC8ContPoint, HUC6ContPoint)
    counter_HUC8 = HUC8
