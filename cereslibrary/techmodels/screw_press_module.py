#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 09:15:46 2018

@author: emh
"""

#screw_press_design
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

def screw_press_module(F_ini,fc_ini,x_ini):
    
    # IMPORT MODULES
    from global_parameters_module import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref, density
    from feedstock_input_module import elements_wet, elements_dry, nutrients, feedstock_parameters, elements_dry_comp
    from equipment_costs.screwpress_cost_module import screw_press_cost_module
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================  
    
    # SETS, PARAMETERS AND NODES DATA ACQUISITION
    nodes_matrix        = pd.read_csv('cereslibrary/techmodels/nodes/nodes_screw_press.csv', sep=",", header=None)
    #nodes_matrix        = pd.read_csv('nodes/nodes_screw_press.csv', sep=",", header=None)
    nodes       = np.array(nodes_matrix[0].dropna())
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================  
    #SCREW PRESS PARAMETERS
    S_slurry_massfrac       = (0.03+0.13)/2 #Solid generated-slurry trated mass fraction kg/kg Moller, Lund and Sommer, 2000
    screwpress_DM_sepindex  = ((0.16+0.33)/2)*(1-S_slurry_massfrac)+S_slurry_massfrac   #DM separation index Moller, Lund and Sommer, 2000
    screwpress_N_sepindex   = ((0.01+0.02)/2)*(1-S_slurry_massfrac)+S_slurry_massfrac    #Organic N separation index Moller, Lund and Sommer, 2000
    screwpress_P_sepindex   = ((0.08+0.23)/2)*(1-S_slurry_massfrac)+S_slurry_massfrac    #It is considered that P separated is Organic P, separation index Moller, Lund and Sommer, 2000
    
    
#    screwpress_max_diameter = 23*UnitConv['inch_to_m']
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================  
    # TOTAL ELEMENTS
    total_elements = elements_wet
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================
    # VARIABLES DEFINITION (IN NESTED DICTIONARIES) (INITIALIZATION)
    nodes_list              = nodes.tolist()
    initialization_comp     = total_elements #["Wa", "C", "NH3", "PO4", "Ca_ion", "K_ion"]
    initialization_nan      = np.full((len(initialization_comp)), 0)
    
    fc = {key: dict(zip(initialization_comp,initialization_nan)) for key in nodes_list}
    
    x = {key: dict(zip(initialization_comp,initialization_nan)) for key in nodes_list}
    
    F = {key: np.nan for key in nodes_list}
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================
    # MASS BALANCE
    for i in total_elements.keys():
#        x["SrcScrewPress"][i]  = x[i]/100
#        fc["SrcScrewPress"][i] = x["SrcScrewPress"][i]*F_ini
        x["SrcScrewPress"][i]  = x_ini[i]
        fc["SrcScrewPress"][i] = fc_ini[i]
    
            
    fc["ScrewPressSink1"]["P"]      = fc["SrcScrewPress"]["P"]*screwpress_P_sepindex
    fc["ScrewPressSink1"]["N"]      = fc["SrcScrewPress"]["N"]*screwpress_N_sepindex
    Aux_Sink1                       = (fc["ScrewPressSink1"]["P"]+fc["ScrewPressSink1"]["N"]+fc["SrcScrewPress"]["Rest"]+fc["SrcScrewPress"]["C"]+fc["SrcScrewPress"]["Ca"]+fc["SrcScrewPress"]["K"])*screwpress_DM_sepindex
    fc["ScrewPressSink1"]["C"]      = Aux_Sink1*(fc["SrcScrewPress"]["C"]/(fc["ScrewPressSink1"]["P"]+fc["ScrewPressSink1"]["N"]+fc["SrcScrewPress"]["Rest"]+fc["SrcScrewPress"]["C"]+fc["SrcScrewPress"]["Ca"]+fc["SrcScrewPress"]["K"]))
    fc["ScrewPressSink1"]["Rest"]   = Aux_Sink1*(fc["SrcScrewPress"]["Rest"]/(fc["ScrewPressSink1"]["P"]+fc["ScrewPressSink1"]["N"]+fc["SrcScrewPress"]["Rest"]+fc["SrcScrewPress"]["C"]+fc["SrcScrewPress"]["Ca"]+fc["SrcScrewPress"]["K"]))
    fc["ScrewPressSink1"]["Ca"]     = Aux_Sink1*(fc["SrcScrewPress"]["Ca"]/(fc["ScrewPressSink1"]["P"]+fc["ScrewPressSink1"]["N"]+fc["SrcScrewPress"]["Rest"]+fc["SrcScrewPress"]["C"]+fc["SrcScrewPress"]["Ca"]+fc["SrcScrewPress"]["K"]))
    fc["ScrewPressSink1"]["K"]      = Aux_Sink1*(fc["SrcScrewPress"]["K"]/(fc["ScrewPressSink1"]["P"]+fc["ScrewPressSink1"]["N"]+fc["SrcScrewPress"]["Rest"]+fc["SrcScrewPress"]["C"]+fc["SrcScrewPress"]["Ca"]+fc["SrcScrewPress"]["K"]))
    DM_Sink1                        = fc["ScrewPressSink1"]["P"]+fc["ScrewPressSink1"]["N"]+fc["ScrewPressSink1"]["C"]+fc["ScrewPressSink1"]["Rest"]+fc["ScrewPressSink1"]["Ca"]+fc["ScrewPressSink1"]["K"]
    fc["ScrewPressSink1"]["Wa"]     = F_ini*S_slurry_massfrac-DM_Sink1
    if fc["ScrewPressSink1"]["Wa"] > 0:
        pass
    else:
        print('ERROR negative fc["ScrewPressSink1"]["Wa"] variable')
    fc["ScrewPressSink1"]["P-PO4"]  = fc["ScrewPressSink1"]["Wa"]*x["SrcScrewPress"]["P-PO4"]
    fc["ScrewPressSink1"]["N-NH3"]  = fc["ScrewPressSink1"]["Wa"]*x["SrcScrewPress"]["N-NH3"]
    fc["ScrewPressSink1"]["Ca_ion"] = fc["ScrewPressSink1"]["Wa"]*x["SrcScrewPress"]["Ca_ion"]
    fc["ScrewPressSink1"]["K_ion"]  = fc["ScrewPressSink1"]["Wa"]*x["SrcScrewPress"]["K_ion"]
    
    fc["ScrewPressSink2"]["P"]          = fc["SrcScrewPress"]["P"]-fc["ScrewPressSink1"]["P"]
    fc["ScrewPressSink2"]["N"]          = fc["SrcScrewPress"]["N"]-fc["ScrewPressSink1"]["N"]
    fc["ScrewPressSink2"]["C"]          = fc["SrcScrewPress"]["C"]-fc["ScrewPressSink1"]["C"]
    fc["ScrewPressSink2"]["Rest"]       = fc["SrcScrewPress"]["Rest"]-fc["ScrewPressSink1"]["Rest"]
    fc["ScrewPressSink2"]["Ca"]         = fc["SrcScrewPress"]["Ca"]-fc["ScrewPressSink1"]["Ca"]
    fc["ScrewPressSink2"]["K"]          = fc["SrcScrewPress"]["K"]-fc["ScrewPressSink1"]["K"]
    fc["ScrewPressSink2"]["Wa"]         = fc["SrcScrewPress"]["Wa"]-fc["ScrewPressSink1"]["Wa"]
    fc["ScrewPressSink2"]["P-PO4"]     = fc["SrcScrewPress"]["P-PO4"]-fc["ScrewPressSink1"]["P-PO4"]      
    fc["ScrewPressSink2"]["N-NH3"]     = fc["SrcScrewPress"]["N-NH3"]-fc["ScrewPressSink1"]["N-NH3"]
    fc["ScrewPressSink2"]["Ca_ion"]    = fc["SrcScrewPress"]["Ca_ion"]-fc["ScrewPressSink1"]["Ca_ion"]
    fc["ScrewPressSink2"]["K_ion"]     = fc["SrcScrewPress"]["K_ion"]-fc["ScrewPressSink1"]["K_ion"]
            
    for i in nodes_list:
        F[i] = sum(fc[i][ii] for ii in elements_wet)
            
    for i in nodes_list:
        if i!="SrcScrewPress":
            for ii in elements_wet.keys():
                x[i][ii] = fc[i][ii]/F[i]
                
    #Checks
    checks_store = ['OK', 'FAIL']
    checks_F = []
    checks_x = []
#    for i in total_elements.keys():
#        if abs(fc["ScrewPressSink1"][i] + fc["ScrewPressSink2"][i] - fc["SrcScrewPress"][i]) <= 0.005:
#            print("fc check", i, "OK")
#        else:
#            print("fc check", i, "FAIL")
    
    if abs(F["ScrewPressSink1"] + F["ScrewPressSink2"] - F["SrcScrewPress"]) <= 0.005:
#        print("F check OK")
        checks_F = checks_store[0]
    else:
#        print("F check FAIL")
        checks_F = checks_store[1]
    
    for i in nodes_list:
        if abs(1-sum(x[i][ii] for ii in total_elements)) <= 0.005:
#            print("x check", i, "OK")
            checks_x = checks_store[0]
        else:
#            print("x check", i, "FAIL")
            checks_x = checks_store[1]
    print("\n\n")
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================

    # ECONOMICS/DESIGN FILTER
    #Size    
    Flow_m3_day = F_ini/(feedstock_parameters['digestate_density']*1000)*3600*24
#    screwpress_diameter_m = 5.91556340e-08*Flow_m3_day**3 - 3.56861865e-05*Flow_m3_day**2 + 6.88383189e-03*Flow_m3_day - 6.09203899e-03#m
#    n_screwpress =np.ceil(screwpress_diameter_m/screwpress_max_diameter)
#    screwpress_desing_flow_m3_day = Flow_m3_day/n_screwpress
#    screwpress_design_diameter_m = 5.91556340e-08*screwpress_desing_flow_m3_day**3 - 3.56861865e-05*screwpress_desing_flow_m3_day**2 + 6.88383189e-03*screwpress_desing_flow_m3_day - 6.09203899e-03#m
#    screwpress_cost_2014_USD = n_screwpress*(23221.804*screwpress_design_diameter_m**2+24708.740*screwpress_design_diameter_m - 2547.881)
#    screwpress_cost_2016_USD = screwpress_cost_2014_USD*(CEI[2016]/CEI[2014])
#    screwpress_PPC_2016_USD = 3.15*screwpress_cost_2016_USD
#    screwpress_FC_2016_USD = 1.4*screwpress_PPC_2016_USD
#    screwpress_operational_cost = n_screwpress*(7.416e-06*screwpress_desing_flow_m3_day**2+2.292e-03*screwpress_desing_flow_m3_day+1.946e-01)*3600*price['electricity'] #USD/year
    ScrewPress_result                   = screw_press_cost_module(Flow_m3_day)
    ScrewPress_diameter                 = ScrewPress_result['ScrewPress_diameter']
    n_ScrewPress                        = ScrewPress_result['n_ScrewPress']
    power_kW_ScrewPress                 = ScrewPress_result['power_kW_ScrewPress']
    equipment_cost                      = ScrewPress_result['equipment_cost']
    investment_cost                     = ScrewPress_result['investment_cost']
    operation_cost_2016_amortized       = ScrewPress_result['operation_cost_2016_amortized']    
    operation_cost_2016_non_amortized   = ScrewPress_result['operation_cost_2016_non_amortized']  
    
    return {'tech' : 'Screw press',
            'Flow_m3_day':Flow_m3_day,'ScrewPress_diameter':ScrewPress_diameter, 'n_ScrewPress':n_ScrewPress, 'power_kW_ScrewPress':power_kW_ScrewPress, 
            'equipment_cost':equipment_cost,
            'investment_cost':investment_cost,
            'operation_cost_2016_amortized':operation_cost_2016_amortized, 
            'operation_cost_2016_non_amortized':operation_cost_2016_non_amortized, 
            'fc':fc,
            'x':x,
            'F':F,
            'checks_F':checks_F,
            'checks_x':checks_x,
            'ScrewPress_diameter':ScrewPress_diameter,
            'n_ScrewPress':n_ScrewPress,
            'power_kW_ScrewPress':power_kW_ScrewPress
            }
