#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 09:15:46 2018

@author: emh
"""

#feedstock_input_module
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

# MANURE DATA ACQUISITION AND COMPOSITION SETTLEMENT
waste_data          = pd.read_csv('cereslibrary/techmodels/feedstock_data/waste_data_input.csv', sep=",", header=0)
#waste_data          = pd.read_csv('feedstock_data/waste_data_input.csv', sep=",", header=0)
input_comp_raw_comp = np.array(waste_data["Component"].dropna()) #NaN removed
input_comp_raw_conc = np.array(waste_data["Concentration"].dropna()) #NaN removed

input_comp_raw  = dict(zip(input_comp_raw_comp, input_comp_raw_conc))
comp_ready      = ["Wa", "OM", "C", "Rest"]
input_comp      = {key:input_comp_raw[key] for key in comp_ready}
input_comp.update({"N":input_comp_raw["N"]*(1-input_comp_raw["NH3_N_ratio"]), 
                   "P":input_comp_raw["P"]*(1-input_comp_raw["PO4_P_ratio"]),
                   "Ca":input_comp_raw["Ca"]*(1-input_comp_raw["Caion_Ca_ratio"]), 
                   "K":input_comp_raw["K"]*(1-input_comp_raw["Kion_K_ratio"]),
                   "N-NH3":input_comp_raw["N"]*input_comp_raw["NH3_N_ratio"], 
                   "P-PO4":input_comp_raw["P"]*input_comp_raw["PO4_P_ratio"], 
                   "Ca_ion":input_comp_raw["Ca"]*input_comp_raw["Caion_Ca_ratio"], 
                   "K_ion":input_comp_raw["K"]*input_comp_raw["Kion_K_ratio"]})

elements_wet_comp   = ["Wa", "C", "N", "P", "Ca", "K", "N-NH3", "P-PO4", "Ca_ion", "K_ion", "Rest"]
elements_dry_comp   = ["C", "N", "P", "Ca", "K", "N-NH3", "P-PO4", "Ca_ion", "K_ion", "Rest"]
nutrients_comp      = ["N-NH3", "P-PO4"]
elements_wet        = {key:input_comp[key] for key in elements_wet_comp} #SUBSET wet digestate elements
elements_dry        = {key:input_comp[key] for key in elements_dry_comp} #SUBSET dry digestate elements
nutrients           = {key:input_comp[key] for key in nutrients_comp} #SUBSET nutrients

# ===============================================================================================================================================================================================================================
# ###############################################################################################################################################################################################################################
# ===============================================================================================================================================================================================================================
# FEDSTOCK PARAMETERS
#feedstock_parameters_matrix          = pd.read_csv('feedstock_data/feedstock_parameters.csv', sep=",", header=0)
feedstock_parameters_matrix          = pd.read_csv('cereslibrary/techmodels/feedstock_data/feedstock_parameters.csv', sep=",", header=0)
feedstock_parameters                 = dict(zip(np.array(feedstock_parameters_matrix["Name"].dropna()), np.array(feedstock_parameters_matrix["Value"].dropna())))
