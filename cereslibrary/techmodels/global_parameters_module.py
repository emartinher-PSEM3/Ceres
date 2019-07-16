#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 09:15:46 2018

@author: emh
"""

#global_parameters_module
#
#Tool for selection of nutrients recovery technologies.
#
#Edgar Martín Hernández.
#
#Cincinnati 2019.


# ===============================================================================================================================================================================================================================
# ###############################################################################################################################################################################################################################
# ===============================================================================================================================================================================================================================
# IMPORT LIBRARIES MODULE
import numpy as np
import pandas as pd
    
pd.options.display.max_columns = 50


# ===============================================================================================================================================================================================================================
# ###############################################################################################################################################################################################################################
# ===============================================================================================================================================================================================================================
# UNIT CONVERSION
UnitConv_matrix = pd.read_csv('cereslibrary/techmodels/global_datasets/units_conversion.csv', sep=",", header=0)
#UnitConv_matrix = pd.read_csv('global_datasets/units_conversion.csv', sep=",", header=0)
UnitConv        = dict(zip(np.array(UnitConv_matrix["Unit"].dropna()), np.array(UnitConv_matrix["Value"].dropna())))

# ===============================================================================================================================================================================================================================
# ###############################################################################################################################################################################################################################
# ===============================================================================================================================================================================================================================
# SETS, PARAMETERS AND NODES DATA ACQUISITION
#    sets_matrix         = pd.read_csv('cereslibrary/techmodels/sets_filtration.csv', sep=",", header=0)#, names=["Units", "Input_Components", "Components"])
#    parameters_matrix   = pd.read_csv('cereslibrary/techmodels/parameters_general.csv', sep=",", header=0)#, names=["Comp", "MW", "c_p_liquid_solid_avg_20to100C", "dH_vap_0",	"Tc",	"Tb",	"dH_f",	"dH_c",	"c_p_v_1", 	"c_p_v_2", 	"c_p_v_3",	"c_p_v_4", 	"coef_vapor_pressure_1", 	"coef_vapor_pressure_2", "coef_vapor_pressure_3"])
##    sets_matrix         = pd.read_csv('sets_filtration.csv', sep=",", header=0)#, names=["Units", "Input_Components", "Components"])
parameters_matrix   = pd.read_csv('cereslibrary/techmodels/global_datasets/parameters_general.csv', sep=",", header=0)
#parameters_matrix   = pd.read_csv('global_datasets/parameters_general.csv', sep=",", header=0)
#, names=["Comp", "MW","c_p_liquid_solid_avg_20to100C", "dH_vap_0",	"Tc",	"Tb",	"dH_f",	"dH_c",	"c_p_v_1", 	"c_p_v_2", 	"c_p_v_3",	"c_p_v_4", 	"coef_vapor_pressure_1", 	"coef_vapor_pressure_2", "coef_vapor_pressure_3"])

MW                      =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["MW"].dropna()))) #NaN removed
c_p_liq_sol             =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["c_p_liquid_solid_avg_20to100C"].dropna()))) #NaN removed
dH_vap_0                =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["dH_vap_0"].dropna()))) #NaN removed
Tc                      =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["Tc"].dropna()))) #NaN removed
Tb                      =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["Tb"].dropna()))) #NaN removed
dH_f                    =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["dH_f"].dropna()))) #NaN removed
dH_c                    =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["dH_c"].dropna()))) #NaN removed
c_p_v_1                 =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["c_p_v_1"].dropna()))) #NaN removed
c_p_v_2                 =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["c_p_v_2"].dropna()))) #NaN removed
c_p_v_3                 =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["c_p_v_3"].dropna()))) #NaN removed
c_p_v_4                 =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["c_p_v_4"].dropna()))) #NaN removed
coef_vapor_pressure_1   =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["coef_vapor_pressure_1"].dropna()))) #NaN removed
coef_vapor_pressure_2   =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["coef_vapor_pressure_2"].dropna()))) #NaN removed
coef_vapor_pressure_3   =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["coef_vapor_pressure_3"].dropna()))) #NaN removed
density                 =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["density"].dropna()))) #NaN removed
latent_heat_evap        =   dict(zip(np.array(parameters_matrix["Comp"].dropna()), np.array(parameters_matrix["latent_heat_evap"].dropna()))) #NaN removed


# ===============================================================================================================================================================================================================================
# ###############################################################################################################################################################################################################################
# ===============================================================================================================================================================================================================================
# Chemical Engineering Index
CEI_matrix = pd.read_csv('cereslibrary/techmodels/global_datasets/CEI_index.csv', sep=",", header=0)
#CEI_matrix = pd.read_csv('global_datasets/CEI_index.csv', sep=",", header=0)
CEI        = dict(zip(np.array(CEI_matrix["Year"].dropna()), np.array(CEI_matrix["Value"].dropna())))

# ===============================================================================================================================================================================================================================
# ###############################################################################################################################################################################################################################
# ===============================================================================================================================================================================================================================
# PRICES
price_matrix = pd.read_csv('cereslibrary/techmodels/global_datasets/prices.csv', sep=",", header=0)
#price_matrix = pd.read_csv('global_datasets/prices.csv', sep=",", header=0)
price        = dict(zip(np.array(price_matrix["Item"].dropna()), np.array(price_matrix["Value"].dropna())))

# ===============================================================================================================================================================================================================================
# ###############################################################################################################################################################################################################################
# ===============================================================================================================================================================================================================================
# OTHERS
nu_p        =   0.80    #polytropic efficiency
k_p         =   1.4     #polytropic coefficient
n_watson    =   0.38    #exponent in Watson correlation
epsilon     =   1E-5   #small number to avoid div. by zero

T_amb = 25+273
P_ref = 1E5

nat_gas_heat_value = 38002.14867 # KJ/m3 https://www.eia.gov/dnav/ng/ng_cons_heat_a_EPG0_VGTH_btucf_a.htm






    
    
    
