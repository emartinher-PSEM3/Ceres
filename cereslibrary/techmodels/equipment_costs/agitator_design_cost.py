import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def agitator_design_cost (mixing_operation, Volume, n_vessels):
    from global_parameters_module import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref, density, latent_heat_evap, nat_gas_heat_value
    from feedstock_input_module import elements_wet, elements_dry, nutrients, feedstock_parameters, elements_dry_comp
    
    #PARAMETERS
    operation=np.array(['Blending','Homogeneous reaction','Reaction with heat transfer','Liquid-liquid mixtures','Liquid-gas mixtures','Slurries']) #Walas 2012
    specific_power = np.array([0.35,1,3.25,5,7.5,10]) #(HP per 1000gal. Type of fluid: slurries). Agitator power. Rule of thumb. Heuristics in Chemical Engineering. Material from Chemical Process Equipment Selection and Design. Walas, 2012   
    agitator_specific_power = dict(zip(operation, specific_power))
    
    #agitator_coef   = [8.82, 0.1235, 0.0818] # Walas 2012 motor cost estimation agitator coefficients 
    agitator_coef   = [9.25, 0.2801, 0.0542] # Walas 2012 motor cost estimation agitator coefficients (speed 1, ss 316, dual impeller)


    #-------------------------Agitator power----------------------------------
    agitator_power = Volume*UnitConv['m3_to_USgalon']*(agitator_specific_power[mixing_operation]/1000)#(HP)
    n_agitators = n_vessels

    #-------------------------Agitator cost----------------------------------
    cost_agitator_2009 = n_vessels*(1.218*np.exp(agitator_coef[0]+agitator_coef[1]*np.log(agitator_power)+agitator_coef[2]*(np.log(agitator_power))**2)) #($)
    cost_agitator_2016 = cost_agitator_2009*(CEI[2016]/CEI[2009])
    
    #-------------------------Agitator operation cost----------------------------------
    operation_cost_agitator_2016 = agitator_power*UnitConv['HP_to_kW']*price['electricity']*3600*24*365/3600
    
    
    return {'agitator_power':agitator_power, 'n_agitators':n_agitators, 'cost_agitator_2016':cost_agitator_2016, 'operation_cost_agitator_2016':operation_cost_agitator_2016}   
    

