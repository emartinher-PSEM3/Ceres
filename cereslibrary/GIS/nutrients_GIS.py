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

from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize

import geopandas
from geopandas.tools import sjoin
import geoplot as gplt
import geoplot.crs as gcrs

#NARS
NARS_points = pd.read_csv('NRSA 08-09.csv', sep=",", header=0)
NARS_site_info = pd.read_csv('NARS_site_info/siteinfo_0.csv', sep=",", header=0)

NARS_site_info_UIDindex = NARS_site_info.set_index('UID', drop=True)
gdf_NARS_site_info_UIDindex = geopandas.GeoDataFrame(NARS_site_info_UIDindex, geometry=geopandas.points_from_xy(NARS_site_info_UIDindex.LON_DD83, NARS_site_info_UIDindex.LAT_DD83))
gdf_NARS_site_info_UIDindex.crs = {'init' :'epsg:4326'}

#NLA
NLA_points = pd.read_csv('nla2012_waterchem_wide.csv', sep=",", header=0)
NLA_site_info = pd.read_csv('NLA_site_info/nla2012_wide_siteinfo_08232016.csv', sep=",", header=0)

#HUC8
watershed_metadata = pd.read_csv('watershed_metadata/huc8sum_20140326.csv', sep=",", header=0)
HUC8  = geopandas.GeoDataFrame.from_file('watershed/huc8sum.shp')
HUC8.crs = {'init' :'epsg:4326'}

#Ecoregions
Ecoregions  = geopandas.GeoDataFrame.from_file('NARS_NP_values/narswsa_20110504.shp')
Ecoregions.crs = {'init' :'epsg:4326'}


#NARS points
#proj = gcrs.AlbersEqualArea()
#ax = gplt.polyplot(HUC8, projection=proj)
#gplt.pointplot(gdf_NARS_site_info_UIDindex, ax=ax, projection=proj, s=1, c='red')
#plt.savefig('prueba2.pdf')

#gdf_NARS_site_info_UIDindex_renamed = gdf_NARS_site_info_UIDindex.rename(columns={'HUC8':'HUC_8'})



# =============================================================================
# NARS (rivers and streams)
# =============================================================================

# UID_HUC8_dict
UID_HUC8_dict = {key: NARS_site_info['HUC8'][NARS_site_info.UID == key].values for key in NARS_site_info['UID'].values}
UID_XLAT_DD_dict = {key: NARS_site_info['XLAT_DD'][NARS_site_info.UID == key].values for key in NARS_site_info['UID'].values}
UID_XLON_DD_dict = {key: NARS_site_info['XLON_DD'][NARS_site_info.UID == key].values for key in NARS_site_info['UID'].values}
UID_AGGR_ECO9_2015_dict = {key: (NARS_site_info['AGGR_ECO9_2015'][NARS_site_info.UID == key].values) for key in NARS_site_info['UID'].values}

aux_list_HUC8 = []
aux_list_XLAT_DD = []
aux_list_XLON_DD = []
aux_list_AGGR_ECO9_2015 = []
for i in NARS_points['UID']:
    aux_list_HUC8.append(int(UID_HUC8_dict[i]))
    aux_list_XLAT_DD.append(float(UID_XLAT_DD_dict[i]))
    aux_list_XLON_DD.append(-1*float(UID_XLON_DD_dict[i]))
    aux_list_AGGR_ECO9_2015.append(str(UID_AGGR_ECO9_2015_dict[i]))
    
NARS_points['HUC8'] = aux_list_HUC8
NARS_points['XLAT_DD'] = aux_list_XLAT_DD
NARS_points['XLON_DD'] = aux_list_XLON_DD
NARS_points['AGGR_ECO9_2015'] = aux_list_AGGR_ECO9_2015
NARS_points[['UID','HUC8','XLAT_DD','XLON_DD']]

NARS_points = NARS_points.rename(columns={'HUC8':'HUC_8'})
NARS_points_filt_P = NARS_points.dropna(subset=['PTL']) #remove NAN values of PTL
NARS_group_aux = NARS_points_filt_P.groupby(['HUC_8']).mean()

HUC8['HUC_8']=HUC8['HUC_8'].astype(int)
HUC8.to_csv('HUC8.csv', index=False)
HUC8_NARS = HUC8.merge(NARS_group_aux, on='HUC_8')
HUC8_NARS.to_csv('HUC8_NARS.csv', index=False)

#proj = gcrs.AlbersEqualArea()
#norm = colors.LogNorm()
#gplt.choropleth(HUC8_NARS, hue='PTL', projection=proj, norm=norm, cmap='Greens', k=5, scheme='percentiles', legend=True,linewidth=1)
#plt.savefig('prueba3.pdf')

##proj = gcrs.AlbersEqualArea()
##HUC8_NARS_raw = HUC8.merge(NARS_points, on='HUC_8')
##gplt.aggplot(HUC8_NARS_raw, projection=proj, hue='PTL', cmap='Greens', scheme='percentiles', legend=True,linewidth=1,  by='HUC_8', geometry=HUC8)
##plt.savefig('prueba3_1.pdf')


# =============================================================================
# NLA (lakes) UID:HUC8 correspondence
# =============================================================================

# UID_HUC8_dict
UID_HUC8_dict_NLA = {key: NLA_site_info['HUC8'][NLA_site_info.UID == key].values for key in NLA_site_info['UID'].values}
UID_LAT_DD83_dict_NLA = {key: NLA_site_info['LAT_DD83'][NLA_site_info.UID == key].values for key in NLA_site_info['UID'].values}
UID_LON_DD83_dict_NLA = {key: NLA_site_info['LON_DD83'][NLA_site_info.UID == key].values for key in NLA_site_info['UID'].values}
UID_AGGR_ECO9_2015_dict_NLA = {key: NLA_site_info['AGGR_ECO9_2015'][NLA_site_info.UID == key].values for key in NLA_site_info['UID'].values}

aux_list_HUC8_NLA = []
aux_list_LAT_DD83_NLA = []
aux_list_LON_DD83_NLA = []
aux_list_AGGR_ECO9_2015_NLA = []
for i in NLA_points['UID']:
    aux_list_HUC8_NLA.append(int(UID_HUC8_dict_NLA[i]))
    aux_list_LAT_DD83_NLA.append(float(UID_LAT_DD83_dict_NLA[i]))
    aux_list_LON_DD83_NLA.append(float(UID_LON_DD83_dict_NLA[i]))
    aux_list_AGGR_ECO9_2015_NLA.append(str(UID_AGGR_ECO9_2015_dict_NLA[i]))
    
NLA_points['HUC8'] = aux_list_HUC8_NLA
NLA_points['LAT_DD83'] = aux_list_LAT_DD83_NLA
NLA_points['LON_DD83'] = aux_list_LON_DD83_NLA
NLA_points['AGGR_ECO9_2015'] = aux_list_AGGR_ECO9_2015_NLA
NLA_points[['UID','HUC8','LAT_DD83','LON_DD83', 'AGGR_ECO9_2015']]

NLA_points = NLA_points.rename(columns={'HUC8':'HUC_8', 'PTL_RESULT':'PTL', 'AMMONIA_N_RESULT':'NH4'})
NLA_points_filt_P = NLA_points.dropna(subset=['PTL']) #remove NAN values of PTL
NLA_group_aux = NLA_points_filt_P.groupby(['HUC_8']).mean()
NLA_P = NLA_group_aux['PTL']

HUC8_NLA = HUC8.merge(NLA_group_aux, on='HUC_8')

#proj = gcrs.AlbersEqualArea()
#norm = colors.LogNorm()
#gplt.choropleth(HUC8_NLA, hue='PTL', projection=proj, norm=norm, cmap='Greens', k=5, scheme='percentiles', legend=True)#, linewidth=0.5, edgecolor='black',)
#plt.savefig('prueba4.pdf')


# =============================================================================
# NARS+NLA
# =============================================================================

NARS_NLA_points = pd.concat([NARS_points, NLA_points], ignore_index=True, sort=False)
NARS_NLA_points_filt_P = NARS_NLA_points.dropna(subset=['PTL']) #remove NAN values of PTL
NARS_NLA_group_aux = NARS_NLA_points_filt_P.groupby(['HUC_8']).mean()

HUC8_NARS_NLA = HUC8.merge(NARS_NLA_group_aux, on='HUC_8')
#
#proj = gcrs.AlbersEqualArea()
#norm = colors.LogNorm()
#gplt.choropleth(HUC8_NARS_NLA, hue='PTL', projection=proj, norm=norm, cmap='Greens', k=5, scheme='percentiles', legend=True)#, linewidth=0.5, edgecolor='black',)
#plt.savefig('prueba5.pdf')


# =============================================================================
# Fill the gaps with the ecoregions average data
# =============================================================================
HUC8_in_NARS_NLA_list = list(HUC8_NARS_NLA['HUC_8'])
HUC8_total_list = list(HUC8['HUC_8'])
HUC8_diff_list = set(HUC8_total_list)-set(HUC8_in_NARS_NLA_list)

HUC8_diff = HUC8[HUC8['HUC_8'].isin(HUC8_diff_list)]

HUC8inEcoregions = sjoin(HUC8_diff, Ecoregions, how='inner', op='intersects')
HUC8inEcoregions = HUC8inEcoregions.drop_duplicates(subset=['HUC_8'])
HUC8inEcoregions_index = HUC8inEcoregions.set_index('HUC_8')

HUC8_Ecoregion_dict = dict(zip(HUC8inEcoregions.HUC_8, HUC8inEcoregions.WSA_REGION))

NARS_NLA_AGGR_ECO9_2015 = NARS_NLA_points.groupby(['AGGR_ECO9_2015']).mean()
NARS_NLA_AGGR_ECO9_2015 = NARS_NLA_AGGR_ECO9_2015.rename(index={"['CPL']":'CPL',
                                      "['NAP']":'NAP',
                                      "['NPL']":'NPL',
                                      "['SAP']":'SAP',
                                      "['SPL']":'SPL',
                                      "['TPL']":'TPL',
                                      "['UMW']":'UMW',
                                      "['WMT']":'WMT',
                                      "['XER']":'XER',
                                     })
    
HUC8_Ecoregion_PTL_dict = dict()
for l in HUC8_diff.HUC_8:
    HUC8_Ecoregion_PTL_dict[l] = NARS_NLA_AGGR_ECO9_2015.loc[HUC8_Ecoregion_dict[l],'PTL']
    
HUC8_Ecoregion_NH4_dict = dict()
for l in HUC8_diff.HUC_8:
    HUC8_Ecoregion_NH4_dict[l] = NARS_NLA_AGGR_ECO9_2015.loc[HUC8_Ecoregion_dict[l],'NH4']

#Average ecoregion value    
#HUC8_Ecoregion_PTL = pd.DataFrame(HUC8_Ecoregion_PTL_dict.items(), columns=['HUC_8', 'PTL'])
#HUC8_Ecoregion_NH4 = pd.DataFrame(HUC8_Ecoregion_NH4_dict.items(), columns=['HUC_8', 'NH4'])
#HUC8_Ecoregion = pd.merge(HUC8_Ecoregion_PTL, HUC8_Ecoregion_NH4, how='inner', on='HUC_8')
#HUC8_Ecoregion = HUC8_Ecoregion.set_index('HUC_8', drop=True)
#
#NARS_NLA_FINAL = pd.concat([NARS_NLA_group_aux, HUC8_Ecoregion], ignore_index=False, sort=False)
#
#HUC8_NARS_NLA_FINAL = HUC8.merge(NARS_NLA_FINAL, on='HUC_8')

#proj = gcrs.AlbersEqualArea()
#norm = colors.LogNorm()
#gplt.choropleth(HUC8_NARS_NLA_FINAL, hue='PTL', projection=proj, norm=norm, cmap='viridis', k=5, scheme='quantiles', legend=True, legend_kwargs={'loc': 'lower right'},figsize=(12, 12))#, linewidth=0.5, edgecolor='black',)
#plt.savefig('prueba6.pdf')
#plt.savefig("obesity.png", bbox_inches='tight', pad_inches=0.1)

   
#Zeros
HUC8_Ecoregion_PTL = pd.DataFrame(HUC8_diff.HUC_8, columns=['HUC_8'])
HUC8_Ecoregion_PTL['PTL'] = 0

HUC8_Ecoregion_NH4 = pd.DataFrame(HUC8_diff.HUC_8, columns=['HUC_8'])
HUC8_Ecoregion_NH4['NH4'] = 0

HUC8_Ecoregion = pd.merge(HUC8_Ecoregion_PTL, HUC8_Ecoregion_NH4, how='inner', on='HUC_8')
HUC8_Ecoregion = HUC8_Ecoregion.set_index('HUC_8', drop=True)

NARS_NLA_FINAL = pd.concat([NARS_NLA_group_aux, HUC8_Ecoregion], ignore_index=False, sort=False)

HUC8_NARS_NLA_FINAL = HUC8.merge(NARS_NLA_FINAL, on='HUC_8')

proj = gcrs.AlbersEqualArea()
norm = colors.LogNorm()
#cmap = matplotlib.cm.viridis
#cmap=matplotlib.cm.get_cmap()
cmap.set_under('grey')
gplt.choropleth(HUC8_NARS_NLA_FINAL, hue='PTL', projection=proj, norm=norm, cmap='viridis', k=5, scheme='quantiles', legend=True, legend_kwargs={'loc': 'lower right'},figsize=(12, 12), vmin=0.8)#, vmin=0.8, vmax=HUC8_NARS_NLA_FINAL['PTL'].max() , linewidth=0.5, edgecolor='black',)
plt.savefig('prueba6_1.pdf')
plt.savefig("obesity.png", bbox_inches='tight', pad_inches=0.1)


    