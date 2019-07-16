import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def BeltFilt_design_cost (F_filtrate):
    from global_parameters_module import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref, density, latent_heat_evap, nat_gas_heat_value
    from feedstock_input_module import elements_wet, elements_dry, nutrients, feedstock_parameters, elements_dry_comp

    #PARAMETERS
    #Belt filter parameters
    filt_rate  = 40/3600 #FILTRATE rate kg/(m2*s) Walas 2012
    max_size = 1200

    #-------------------------Belt filter dimensions----------------------------------
    Area = F_filtrate/filt_rate #m2

    #-------------------------Belt filter cost----------------------------------------
    n_filt = []
    if Area*UnitConv['m2_to_ft2'] > max_size:
        n_filt = np.ceil((Area*UnitConv['m2_to_ft2'])/max_size)
        Area = max_size/UnitConv['m2_to_ft2']
        BeltFilt_cost_2016 = n_filt*(45506/((Area*UnitConv['m2_to_ft2'])**0.50)*Area*UnitConv['m2_to_ft2']*(CEI[2016]/CEI[2009])) #Walas 2012
        
    elif Area*UnitConv['m2_to_ft2'] <= max_size:
        n_filt = 1
        BeltFilt_cost_2016 = n_filt*(45506/((Area*UnitConv['m2_to_ft2'])**0.50)*Area*UnitConv['m2_to_ft2']*(CEI[2016]/CEI[2009])) #Walas 2012
    
    
    return {'Area':Area, 'n_filt':n_filt, 'BeltFilt_cost_2016':BeltFilt_cost_2016}   
    

