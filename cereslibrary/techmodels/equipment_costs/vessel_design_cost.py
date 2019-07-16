import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def vessel_design_cost (F_total, residence_time):
    from global_parameters_module import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref, density, latent_heat_evap, nat_gas_heat_value
    from feedstock_input_module import elements_wet, elements_dry, nutrients, feedstock_parameters, elements_dry_comp

    #PARAMETERS
    #Vessel parameters
    SS_316_density              = 7.99 #SS 316 density (kg/L) http://www.aksteel.com/pdf/markets_products/stainless/austenitic



    #-------------------------Vessel dimensions----------------------------------
    Volume = (F_total/feedstock_parameters['digestate_density'])*UnitConv['L_to_m3']*residence_time #m3

    max_size = 45 #CapCost
    V_design = []
    n_vessels    =[]
    if Volume <= max_size:
        V_design = Volume
        n_vessels   = 1
    elif Volume > max_size:
        V_design = max_size
        n_vessels  = np.ceil(Volume/max_size)

    #D_design = ((6*V_design)/(7*np.pi))**(1/3) #m for L=4D
    D_design = ((4*V_design)/(1.2*np.pi))**(1/3) #m for L=1.2D
    L_design = 1.2*D_design #m Fluid dynamic concepts for a phosphate precipitation reactor design. D. Mangin and J.P. Klein. Phosphorus in Environmental Technology Principles and Applications Valsami-Jones
    e = 0.0023+0.003*D_design #m Martin and Almena 2016
    Weight = SS_316_density/UnitConv['L_to_m3']*(np.pi*(((D_design/2)+e)**2-(D_design/2)**2)*L_design+(4/3)*np.pi*(((D_design/2)+e)**3-(D_design/2)**3)) #kg Martin and Almena 2016

    #-------------------------Vessel cost----------------------------------
    #normalized_D = np.array([3, 4.5, 6, 7.5, 9]) #m, API Standard 650
    #normalized_L = np.array([3.6, 5.4, 7.2, 9, 10.8]) #m, API Standard 650, L = D #m Fluid dynamic concepts for a phosphate precipitation reactor design. D. Mangin and J.P. Klein. Phosphorus in Environmental Technology Principles and Applications Valsami-Jones
    #D_design    =[]
    #n_vessels    =[]
    #loop_break = False

    #if D <= max(normalized_D):
        #for i in normalized_D:
            #if D/i <= 1:
                #D_design    = i
                #n_vessels   = 1
                #loop_break = True
                #break
            #if loop_break: break
    #elif D/ max(normalized_D) <= 2:
        #aux1 = [i for i in normalized_D if i*2 > max(normalized_D)]
        #for i in aux1:
            #if D/i <= 2:
                #D_design    = i
                #n_vessels   = 2
                #loop_break = True
                #break
            #if loop_break: break
    #elif D/ max(normalized_D) > 2:
        #D_design = max(normalized_D)
        #n_vessels = np.ceil(D/max(normalized_D))

    #L_design = []   
    #for i in normalized_D:
            #if D_design/i == 1:
                #L_design = np.asscalar(normalized_L[np.where(normalized_D == i)])
        
    vessels_cost_2016 = n_vessels*(-6.15670995670996*V_design**2 + 1276.0354978355*V_design+ 4007.61904761903) #CapCost 
    
    
    return {'Volume':Volume, 'V_design':V_design, 'D_design':D_design, 'L_design':L_design, 'n_vessels':n_vessels, 'vessels_cost_2016':vessels_cost_2016}   
    

