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

def AD_cost_module(N_animals):
    
    # IMPORT MODULES
    from global_parameters_module import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref, density, latent_heat_evap, nat_gas_heat_value
    from feedstock_input_module import elements_wet, elements_dry, nutrients, feedstock_parameters, elements_dry_comp
    from economic_parameters_module import ec_param
    
    AD_investment_cost = (427.107*N_animals+126958.208)*(CEI[2016]/CEI[2003])
    
    a=15858.710
    b=13.917
    c=1.461
    OM_unit_cost_ratio = a/(1+((N_animals)*b)**(c))
    OM_cost =  AD_investment_cost*OM_unit_cost_ratio*(CEI[2016]/CEI[2006])
    
    
    operation_cost_2016_amortized = OM_cost + AD_investment_cost/ec_param['plant_lifetime']
    operation_cost_2016_non_amortized = OM_cost
    

    return {'investment_cost':AD_investment_cost,
            'OM_unit_cost_ratio':OM_unit_cost_ratio,
            'OM_cost':OM_cost,
            'operation_cost_2016_amortized':operation_cost_2016_amortized,   
            'operation_cost_2016_non_amortized':operation_cost_2016_non_amortized,  
            }



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
