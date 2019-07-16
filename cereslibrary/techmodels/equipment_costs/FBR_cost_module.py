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
# IMPORT LIBRARIES MODULE
import numpy as np
import pandas as pd
import scipy.optimize as opt
from scipy.integrate import odeint, solve_bvp
import matplotlib.pyplot as plt

pd.options.display.max_columns = 50

#F_tot=1 #kg/s
#fc_P_PO4 = 0.00031919000000000001
#fc_N_NH4 = 0.0022656
#fc_Ca_ion = 0.00018018
#fc_MgCl2 = 0.0019606709090322582
#fc_struvite = 0.0019285752044940962
#NH4_molar = 0.04124722 
#Mg_molar = 0.002562
#PO4_molar = 0.00043357894736842102

def FBR_cost_module(fc_struvite):
    
    # IMPORT MODULES
    from global_parameters_module import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref, density, latent_heat_evap, nat_gas_heat_value
    from feedstock_input_module import elements_wet, elements_dry, nutrients, feedstock_parameters, elements_dry_comp

    #ec_param_matrix = pd.read_csv('economic_datasheets/operation_parameters.csv', sep=",", header=0)
    ec_param_matrix = pd.read_csv('cereslibrary/techmodels/economic_datasheets/operation_parameters.csv', sep=",", header=0)
    ec_param        = dict(zip(np.array(ec_param_matrix["Item"].dropna()), np.array(ec_param_matrix["Value"].dropna())))

    # ====================================================
    # ####################################################
    # ====================================================
    #INPUT CONCENTRATIONS

    #NH4_molar = (fc_N_NH4/MW["N"])
    #Mg_molar = fc_MgCl2/MW["MgCl2"]
    #PO4_molar = fc_P_PO4/MW["P"] 
    #Ca_molar = fc_Ca_ion/MW["Ca"] 
    Struvite_molar = fc_struvite/MW['Struvite']

    #Ca_PO4_ratio = Ca_molar/PO4_molar
    PO4_struvite_molar = Struvite_molar

    # ====================================================
    # ####################################################
    # ====================================================
    #SIZE DETERMINATION (OSTARA)
    daily_PO4_recovered = PO4_struvite_molar*MW['PO4']*3600*24

    FBR_size_array = ['FBR_small: PEARL 500','FBR_medium: PEARL 2K','FBR_large: PEARL 10K']
    FBR_sizes_threshold = [65, 250, 1250]

    FBR_size = []

    if daily_PO4_recovered <= FBR_sizes_threshold[0]:
        FBR_size = FBR_size_array[0]
        
    elif FBR_sizes_threshold[0] < daily_PO4_recovered <= 2*FBR_sizes_threshold[1]:
        FBR_size = FBR_size_array[1]
        
    elif 2*FBR_sizes_threshold[1] < daily_PO4_recovered <= FBR_sizes_threshold[2]:
        FBR_size = FBR_size_array[2]
        
    elif FBR_sizes_threshold[2] < daily_PO4_recovered <= (2*FBR_sizes_threshold[2]+FBR_sizes_threshold[1]):
        FBR_size = [FBR_size_array[1], FBR_size_array[2]]
        
    elif daily_PO4_recovered > FBR_sizes_threshold[2]:
        FBR_size = FBR_size_array[2]

        
    #NUMBER OF UNITS
    n_FBR = []

    if daily_PO4_recovered <= FBR_sizes_threshold[1]:
        n_FBR = 1
        
    elif FBR_sizes_threshold[1] < daily_PO4_recovered <= (2*FBR_sizes_threshold[1]):
        n_FBR = 2

    elif (2*FBR_sizes_threshold[1]) < daily_PO4_recovered <= FBR_sizes_threshold[2]:
        n_FBR = 1
        
    elif FBR_sizes_threshold[2] < daily_PO4_recovered <= (FBR_sizes_threshold[1] + FBR_sizes_threshold[2]):
        n_FBR = 2
        
    elif FBR_sizes_threshold[2] < daily_PO4_recovered <= (2*FBR_sizes_threshold[1] + FBR_sizes_threshold[2]):
        n_FBR = 3
        
    elif daily_PO4_recovered > (2*FBR_sizes_threshold[1] + FBR_sizes_threshold[2]):
        n_FBR = np.ceil(daily_PO4_recovered/FBR_sizes_threshold[2])


    # ====================================================
    # ####################################################
    # ====================================================
    #Unit cost(OSTARA) includes all the system
    FBR_cost = {'FBR_small: PEARL 500':2.3E6, 'FBR_medium: PEARL 2K':3.06E6, 'FBR_large: PEARL 10K':10E6} #USD

    FBR_equipment_cost = FBR_cost[FBR_size]*n_FBR #Total installation

    # ====================================================
    # ####################################################
    # ====================================================
    #OPERATION COST (except chemicals)
    electricity_demand = 220 #kWh/reactor/day
    labor = 2 #hour/reactor/day
    maintenance = 21000 #USD/reactor/year

    FBR_operating_cost_partial = (electricity_demand*price['electricity']*334+labor*ec_param['salary']/49/5/8*334+maintenance)*n_FBR

    return {'FBR_size':FBR_size, 'n_FBR':n_FBR, 'FBR_equipment_cost':FBR_equipment_cost, 'FBR_operating_cost_partial':FBR_operating_cost_partial}



# plot results
#plt.figure()
#plt.plot(H_inverse, L)
#plt.xlabel('Height (m)')
#plt.ylabel('L(H) (m)')
#plt.show()

#plt.figure()
#plt.plot(H, C)
#plt.xlabel('Height (m)')
#plt.ylabel('C(H) (mol/L)')
#plt.show()

#plt.figure()
#plt.plot(H, result.y[0])
#plt.xlabel('Height (m)')
#plt.ylabel('L(H) (m)')
#plt.show()
