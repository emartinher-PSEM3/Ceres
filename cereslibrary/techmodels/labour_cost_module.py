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

# IMPORT LIBRARIES
import numpy as np
import pandas as pd
pd.options.display.max_columns = 50

# ===============================================================================================================================================================================================================================
# ###############################################################################################################################################################################################################################
# ===============================================================================================================================================================================================================================
def labour_cost_module(N_solids_steps, N_compressors, N_towers, N_reactors, N_heaters, N_exchangers):
    
#    ec_param_matrix = pd.read_csv('economic_datasheets/operation_parameters.csv', sep=",", header=0)
    ec_param_matrix = pd.read_csv('cereslibrary/techmodels/economic_datasheets/operation_parameters.csv', sep=",", header=0)
    ec_param        = dict(zip(np.array(ec_param_matrix["Item"].dropna()), np.array(ec_param_matrix["Value"].dropna())))
    
    specific_operator = (ec_param['worked_days']*ec_param['shifts_day'])/(ec_param['worked_weeks_operator']*ec_param['worked_shifts_week']) #Total operators per for each operator needed in the plant
    
    N_np = N_compressors + N_towers + N_reactors + N_heaters + N_exchangers
    N_ol = (6.29+31.7*N_solids_steps**2+0.23*N_np)**0.5
    
    operating_labor = np.ceil(specific_operator*N_ol)
    
    labor_cost = operating_labor*ec_param['salary']
    
    
       
    return {'labor_cost':labor_cost, 'operating_labor':operating_labor}

    



