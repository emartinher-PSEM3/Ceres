import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def ConveyorDryer_design_cost (F_product, fc_Wa):
    from global_parameters_module import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref, density, latent_heat_evap, nat_gas_heat_value
    from feedstock_input_module import elements_wet, elements_dry, nutrients, feedstock_parameters, elements_dry_comp

    #DRYER (Conveyor-Screen-Dryer / Continuous Through-Circulation Dryer) (Table 12-21 Perry)
    drying_time = (12+18/2)/1E-2 #s
    dryer_capacity = (16+25.7)/2 #kg product/m2
    nat_gas_eff = 0.8 # nat gas efficiency, Analysis, Synthesis, and Design of Chemical Processes
    
    max_size = 90 #m2 (Table 12-23 Perry)

    #-------------------------Conveyor dryer dimensions----------------------------------
    #evaporation_capacity = (4536/(66.42*3600)) #  (kg/s-m2) (source: Walas, 1990)
    #
    #Dryer_cost_2007 = 1.15*(6477.1*(fc["BeltFiltDryer"]["Wa"]/evaporation_capacity) + 102394)
    #Dryer_cost_2016 = Dryer_cost_2007*(CEI_2016/CEI_2007)
        
    dryer_loading   = F_product*drying_time
    dryer_area_m2   = dryer_loading/dryer_capacity
    
    #-------------------------Conveyor dryer cost----------------------------------------
    n_dryer = []
    if dryer_area_m2 <= max_size:
        n_dryer = 1
    
    elif dryer_area_m2 > max_size:
        n_dryer = np.ceil(dryer_area_m2/max_size)
        dryer_area_m2 = max_size
        
    ConveyorDryer_cost_1996 = n_dryer*(4582.222*dryer_area_m2 + 63112.5) #(Table 12-23 Perry)
    ConveyorDryer_cost_2016 = ConveyorDryer_cost_1996*(CEI[2016]/CEI[1996])
    
    #-------------------------Conveyor dryer operation cost------------------------------
    Q_latent = fc_Wa*latent_heat_evap['Wa'] #kJ/s
    nat_gas = (Q_latent/nat_gas_heat_value)/nat_gas_eff #m3/s
    nat_gas_cost = nat_gas*price['natural_gas']*3600*24*365 #USD/year
        
    return {'Area':dryer_area_m2, 'n_dryer':n_dryer, 'ConveyorDryer_cost_2016':ConveyorDryer_cost_2016, 'ConveyorDryer_operating_cost_2016':nat_gas_cost}   
    
