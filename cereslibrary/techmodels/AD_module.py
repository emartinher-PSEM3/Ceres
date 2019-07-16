#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 09:15:46 2018

@author: emh
"""

#Ceres_AD_module_v1.
#
#Tool for selection of nutrients recovery technologies.
#
#Edgar Martín Hernández.
#
#Cincinnati 2019.

# IMPORT LIBRARIES
import numpy as np
from scipy import optimize
import pandas as pd
pd.options.display.max_columns = 50


# ===============================================================================================================================================================================================================================
# ###############################################################################################################################################################################################################################
# ===============================================================================================================================================================================================================================
def AD_module(F_ini,fc_ini, x_ini, N_animals):
        
    # IMPORT MODULES
    from global_parameters_module import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref, density, latent_heat_evap, nat_gas_heat_value
    from feedstock_input_module import elements_wet, elements_dry, nutrients, feedstock_parameters
    from equipment_costs.AD_cost_module import AD_cost_module
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================
    # SETS, PARAMETERS AND NODES DATA ACQUISITION
    #nodes_matrix            = pd.read_csv('nodes/nodes_digestor.csv', sep=",", header=None)
    #nodes                   = np.array(nodes_matrix[0].dropna())
    #process_elements_matrix = pd.read_csv('process_elements/process_elements_digestor.csv', sep=",", header=0)
    
    nodes_matrix            = pd.read_csv('cereslibrary/techmodels/nodes/nodes_digestor.csv', sep=",", header=None)
    nodes                   = np.array(nodes_matrix[0].dropna())
    process_elements_matrix = pd.read_csv('cereslibrary/techmodels/process_elements/process_elements_digestor.csv', sep=",", header=0)
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================    
    # MANURE DATA ACQUISITION AND COMPOSITION SETTLEMENT   
    gases_comp   = np.array(process_elements_matrix["Component"].dropna())
    gases_conc   = np.full((len(gases_comp)), 0)
    gases        = dict(zip(gases_comp, gases_conc))
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================  
    # TOTAL ELEMENTS
    total_elements = {**elements_wet,**gases} # Merge the two dictionaries
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================
    # AD PARTICULAR PARAMETERS
    MWDry_CS    =   16          #Other molecular weights
    MWDry_PS    =   14          #Other molecular weights
    MWDry_PoS   =   14.5945     #Other molecular weights
    MWDry_SS    =   14.90306071 #Other molecular weights
    MWDry_D     =   16          #Other molecular weights
    
    dH_cD       =   -216.900    #Heat of combustion of the digestate (kJ/mol)
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================  
    # VARIABLES DEFINITION (IN NESTED DICTIONARIES) (INITIALIZATION)
    nodes_list              = nodes.tolist()
    initialization_comp     = total_elements #["Wa", "C", "NH3", "PO4", "Ca_ion", "K_ion"]
    initialization_nan      = np.full((len(initialization_comp)), 0.00)
    
    fc = {key: dict(zip(initialization_comp,initialization_nan)) for key in nodes_list}
    
    x = {key: dict(zip(initialization_comp,initialization_nan)) for key in nodes_list}
    
    F = {key: np.nan for key in nodes_list}
    
    T = {key: np.nan for key in nodes_list}
    
    y_biogas = {"BioreactorSink1": dict(zip(initialization_comp,initialization_nan)) }
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================     
    # MASS BALANCE
    for i in total_elements.keys():
#        x["Src1Bioreactor"][i]  = total_elements[i]/100
#        fc["Src1Bioreactor"][i] = x["Src1Bioreactor"][i]*F_ini
        x["Src1Bioreactor"][i]  = x_ini[i]
        fc["Src1Bioreactor"][i] = fc_ini[i]
        
    T["Src1Bioreactor"] = T_amb
    #T["Src2Bioreactor"] = T_amb
    T["BioreactorSink1"] = 37
    T["BioreactorSink2"] = 37
    
    MWdrybiogas = feedstock_parameters['Y_CH4']*MW["CH4"]+feedstock_parameters['Y_CO2']* MW["CO2"]+ feedstock_parameters['Y_N2']*MW["N2"]+feedstock_parameters['Y_O2']*MW["O2"]+feedstock_parameters['Y_H2S']*MW["H2S"]+feedstock_parameters['Y_NH3']*MW["NH3"]
    ybiogas= (((np.exp(coef_vapor_pressure_1["Wa"]-coef_vapor_pressure_2["Wa"]/(T["BioreactorSink1"]+coef_vapor_pressure_3["Wa"])))*(10**(5)/750))*(MW["Wa"]))/(((P_ref-(np.exp(coef_vapor_pressure_1["Wa"]-coef_vapor_pressure_2["Wa"]/(T["BioreactorSink1"]+coef_vapor_pressure_3["Wa"])))*(10**(5)/750)))*MWdrybiogas)
    Aux_1=sum(fc["Src1Bioreactor"][i] for i in total_elements)
    
    # =============================================================================
    # #Test parameters
    VbiogasCS_test=0.3
    wVSCS_test=0.8
    wDMCS_test=0.1
    MWdrybiogas_test=24.720
    ybiogas_test=0.136
    T_test=55
    # =============================================================================
    
    def target(j):
    #    return - (((P_ref*(j[16]*1E-3))*(feedstock_parameters['VbiogasCS']*feedstock_parameters['wVSCS']*(1-x["Src1Bioreactor"]['Wa'])*Aux_1))/(8.314*(T["BioreactorSink1"]+273)))
    # =============================================================================
    # #Test function
         return - ((((P_ref*(j[16]*1E-3))*(VbiogasCS_test*wVSCS_test*(wDMCS_test)*Aux_1))/(8.314*(T_test+273))))
    # =============================================================================
    
    # =============================================================================
    # #Test constraints
    cons = (
            {'type':'eq', 'fun': lambda j:j[7] - j[0] - j[1] - j[2] - j[3] - j[4] - j[5]},
            {'type':'eq', 'fun': lambda j:j[0]*MWdrybiogas_test - (feedstock_parameters['Y_CH4']*MW["CH4"])*(((P_ref*(j[16]*1E-3))*(VbiogasCS_test*wVSCS_test*(wDMCS_test)*Aux_1))/(8.314*(T_test+273))-j[6])},
            {'type':'eq', 'fun': lambda j:j[1]*MWdrybiogas_test - (feedstock_parameters['Y_CO2']*MW["CO2"])*(((P_ref*(j[16]*1E-3))*(VbiogasCS_test*wVSCS_test*(wDMCS_test)*Aux_1))/(8.314*(T_test+273))-j[6])},
            {'type':'eq', 'fun': lambda j:j[2]*MWdrybiogas_test - (feedstock_parameters['Y_N2']*MW["N2"])*(((P_ref*(j[16]*1E-3))*(VbiogasCS_test*wVSCS_test*(wDMCS_test)*Aux_1))/(8.314*(T_test+273))-j[6])},
            {'type':'eq', 'fun': lambda j:j[3]*MWdrybiogas_test - (feedstock_parameters['Y_O2']*MW["O2"])*(((P_ref*(j[16]*1E-3))*(VbiogasCS_test*wVSCS_test*(wDMCS_test)*Aux_1))/(8.314*(T_test+273))-j[6])},
            {'type':'eq', 'fun': lambda j:j[4]*MWdrybiogas_test - (feedstock_parameters['Y_H2S']*MW["H2S"])*(((P_ref*(j[16]*1E-3))*(VbiogasCS_test*wVSCS_test*(wDMCS_test)*Aux_1))/(8.314*(T_test+273))-j[6])},
            {'type':'eq', 'fun': lambda j:j[5]*MWdrybiogas_test - (feedstock_parameters['Y_NH3']*MW["NH3"])*(((P_ref*(j[16]*1E-3))*(VbiogasCS_test*wVSCS_test*(wDMCS_test)*Aux_1))/(8.314*(T_test+273))-j[6])},
            {'type':'eq', 'fun': lambda j:j[6] - ybiogas_test*(j[7])},
            {'type':'eq', 'fun': lambda j:j[8] -( j[0]/MW["CH4"]+j[1]/MW["CO2"]+j[2]/MW["N2"]+j[3]/MW["O2"]+j[4]/MW["H2S"]+j[5]/MW["NH3"]+j[6]/MW["Wa"])},
            {'type':'eq', 'fun': lambda j:j[9]*j[8]*MW["CH4"] - j[0]},
            {'type':'eq', 'fun': lambda j:j[10]*j[8]*MW["CO2"] - j[1]},
            {'type':'eq', 'fun': lambda j:j[11]*j[8]*MW["N2"] - j[2]},
            {'type':'eq', 'fun': lambda j:j[12]*j[8]*MW["O2"] - j[3]},
            {'type':'eq', 'fun': lambda j:j[13]*j[8]*MW["H2S"] - j[4]},
            {'type':'eq', 'fun': lambda j:j[14]*j[8]*MW["NH3"] - j[5]},
            {'type':'eq', 'fun': lambda j:j[15]*j[8]*MW["Wa"] - j[6]},
     #        {'type':'eq', 'fun': lambda j:1-(j[9]+j[10]+j[11]+j[12]+j[13]+j[14]+j[15])},
            {'type':'eq', 'fun': lambda j:j[16]-(j[9]*MW["CH4"]+j[10]*MW["CO2"]+j[11]*MW["N2"]+j[12]*MW["O2"]+j[13]*MW["H2S"]+j[14]*MW["NH3"]+j[15]*MW["Wa"])},
     #        {'type':'eq', 'fun': lambda j:(j[7]+j[6])*(8.314*(T["BioreactorSink1"]+273)) - ((P_ref*(j[16]*1E-3))*(VbiogasCS_test*wVSCS_test*(wDMCS_test))*Aux_1)}
            )
    # 
    # =============================================================================
        
    #cons = (
    #        {'type':'eq', 'fun': lambda j:j[7] - j[0] - j[1] - j[2] - j[3] - j[4] - j[5]},
    #        {'type':'eq', 'fun': lambda j:j[0]*MWdrybiogas - (feedstock_parameters['Y_CH4']*MW["CH4"])*((P_ref*(j[16]*1E-3))*(feedstock_parameters['VbiogasCS']*feedstock_parameters['wVSCS']*(1-x["Src1Bioreactor"]['Wa']*Aux_1))/(8.314*(T["BioreactorSink1"]+273))-j[6])},
    #        {'type':'eq', 'fun': lambda j:j[1]*MWdrybiogas - (feedstock_parameters['Y_CO2']*MW["CO2"])*((P_ref*(j[16]*1E-3))*(feedstock_parameters['VbiogasCS']*feedstock_parameters['wVSCS']*(1-x["Src1Bioreactor"]['Wa']*Aux_1))/(8.314*(T["BioreactorSink1"]+273))-j[6])},
    #        {'type':'eq', 'fun': lambda j:j[2]*MWdrybiogas - (feedstock_parameters['Y_N2']*MW["N2"])*((P_ref*(j[16]*1E-3))*(feedstock_parameters['VbiogasCS']*feedstock_parameters['wVSCS']*(1-x["Src1Bioreactor"]['Wa']*Aux_1))/(8.314*(T["BioreactorSink1"]+273))-j[6])},
    #        {'type':'eq', 'fun': lambda j:j[3]*MWdrybiogas - (feedstock_parameters['Y_O2']*MW["O2"])*((P_ref*(j[16]*1E-3))*(feedstock_parameters['VbiogasCS']*feedstock_parameters['wVSCS']*(1-x["Src1Bioreactor"]['Wa']*Aux_1))/(8.314*(T["BioreactorSink1"]+273))-j[6])},
    #        {'type':'eq', 'fun': lambda j:j[4]*MWdrybiogas - (feedstock_parameters['Y_H2S']*MW["H2S"])*((P_ref*(j[16]*1E-3))*(feedstock_parameters['VbiogasCS']*feedstock_parameters['wVSCS']*(1-x["Src1Bioreactor"]['Wa']*Aux_1))/(8.314*(T["BioreactorSink1"]+273))-j[6])},
    #        {'type':'eq', 'fun': lambda j:j[5]*MWdrybiogas - (feedstock_parameters['Y_NH3']*MW["NH3"])*((P_ref*(j[16]*1E-3))*(feedstock_parameters['VbiogasCS']*feedstock_parameters['wVSCS']*(1-x["Src1Bioreactor"]['Wa']*Aux_1))/(8.314*(T["BioreactorSink1"]+273))-j[6])},
    #        {'type':'eq', 'fun': lambda j:j[6] - ybiogas*(j[7])},
    #        {'type':'eq', 'fun': lambda j:j[8] -( j[0]/MW["CH4"]+j[1]/MW["CO2"]+j[2]/MW["N2"]+j[3]/MW["O2"]+j[4]/MW["H2S"]+j[5]/MW["NH3"]+j[6]/MW["Wa"])},
    #        {'type':'eq', 'fun': lambda j:j[9]*j[8]*MW["CH4"] - j[0]},
    #        {'type':'eq', 'fun': lambda j:j[10]*j[8]*MW["CO2"] - j[1]},
    #        {'type':'eq', 'fun': lambda j:j[11]*j[8]*MW["N2"] - j[2]},
    #        {'type':'eq', 'fun': lambda j:j[12]*j[8]*MW["O2"] - j[3]},
    #        {'type':'eq', 'fun': lambda j:j[13]*j[8]*MW["H2S"] - j[4]},
    #        {'type':'eq', 'fun': lambda j:j[14]*j[8]*MW["NH3"] - j[5]},
    #        {'type':'eq', 'fun': lambda j:j[15]*j[8]*MW["Wa"] - j[6]},
    ##        {'type':'eq', 'fun': lambda j:1-(j[9]+j[10]+j[11]+j[12]+j[13]+j[14]+j[15])},
    #        {'type':'eq', 'fun': lambda j:j[16]-(j[9]*MW["CH4"]+j[10]*MW["CO2"]+j[11]*MW["N2"]+j[12]*MW["O2"]+j[13]*MW["H2S"]+j[14]*MW["NH3"]+j[15]*MW["Wa"])},
    ##        {'type':'eq', 'fun': lambda j:(j[7]+j[6])*(8.314*(T["BioreactorSink1"]+273)) - ((P_ref*(j[16]*1E-3))*(feedstock_parameters['VbiogasCS']*feedstock_parameters['wVSCS']*(1-x["Src1Bioreactor"]['Wa'])*Aux_1))}
    #        )
    
    bnds = ((0, None), 
            (0, None),
            (0, None),
            (0, None),
            (0, None),
            (0, None),
            (0, None),
            (0, None),
            (0, None),
            (0, 1),
            (0, 1),
            (0, 1),
            (0, 1),
            (0, 1),
            (0, 1),
            (0, 1),
            (20, 30)
    )
    
    init_vector = np.ones(17)
    sol = optimize.minimize(target, init_vector, method='SLSQP', bounds=bnds, constraints=cons, options={'maxiter':1000})
    
    fc["BioreactorSink1"]["CH4"]    = sol.x[0]
    fc["BioreactorSink1"]["CO2"]    = sol.x[1]
    fc["BioreactorSink1"]["N2"]     = sol.x[2]
    fc["BioreactorSink1"]["O2"]     = sol.x[3]
    fc["BioreactorSink1"]["H2S"]    = sol.x[4]
    fc["BioreactorSink1"]["NH3"]    = sol.x[5]
    fc["BioreactorSink1"]["Wa"]     = sol.x[6]
    mol_total                       = sol.x[8]
    y_biogas["BioreactorSink1"]["CH4"]    = sol.x[9]
    y_biogas["BioreactorSink1"]["CO2"]    = sol.x[10]
    y_biogas["BioreactorSink1"]["N2"]     = sol.x[11]
    y_biogas["BioreactorSink1"]["O2"]     = sol.x[12]
    y_biogas["BioreactorSink1"]["H2S"]    = sol.x[13]
    y_biogas["BioreactorSink1"]["NH3"]    = sol.x[14]
    y_biogas["BioreactorSink1"]["Wa"]     = sol.x[15]
    MWbiogas                              = sol.x[16]
    
    
    
    fc["BioreactorSink2"]["C"] = (fc["Src1Bioreactor"]["C"])-fc["BioreactorSink1"]["CH4"]*(MW["C"]/MW["CH4"])-fc["BioreactorSink1"]["CO2"]*(MW["C"]/MW["CO2"])
    fc["BioreactorSink2"]["N"] = (fc["Src1Bioreactor"]["N"])-fc["BioreactorSink1"]["NH3"]*(MW["N"]/MW["NH3"])
    fc["BioreactorSink2"]["N-NH3"] = fc["Src1Bioreactor"]["N-NH3"]*(1+0.24)
    fc["BioreactorSink2"]["P"] = (fc["Src1Bioreactor"]["P"])
    fc["BioreactorSink2"]["P-PO4"] = fc["Src1Bioreactor"]["P-PO4"]*(1+0.16)
    fc["BioreactorSink2"]["Ca"] = (fc["Src1Bioreactor"]["Ca"])
    fc["BioreactorSink2"]["Ca_ion"] = (fc["Src1Bioreactor"]["Ca_ion"])
    fc["BioreactorSink2"]["K"] = (fc["Src1Bioreactor"]["K"])
    fc["BioreactorSink2"]["K_ion"] = (fc["Src1Bioreactor"]["K_ion"])
    fc["BioreactorSink2"]["Rest"] = (fc["Src1Bioreactor"]["Rest"])
    fc["BioreactorSink2"]["Wa"] = (fc["Src1Bioreactor"]["Wa"])-fc["BioreactorSink1"]["Wa"]
    
    for i in nodes_list:
            F[i] = sum(fc[i][ii] for ii in total_elements)
            
    for i in nodes_list:
        if i!="Src1Bioreactor":
            for ii in total_elements.keys():
                x[i][ii] = fc[i][ii]/F[i]
    
    #    Checks
    checks_store = ['OK', 'FAIL']
    checks_F = []
    checks_x = {}
    
    #for i in total_elements.keys():
        #if abs(fc["BioreactorSink1"][i] + fc["BioreactorSink2"][i] - (fc["Src1Bioreactor"][i]+fc["Src2Bioreactor"][i])) <= 0.01:
            #print("fc check", i, "OK")
        #else:
            #print("fc check", i, "FAIL")
    
    if abs(F["BioreactorSink1"] + F["BioreactorSink2"] - (F["Src1Bioreactor"])) <= 0.1: #+F["Src2Bioreactor"]
        #print("F check OK")
        checks_F = checks_store[0]
    else:
        #print("F check FAIL")
        checks_F = checks_store[1]
    
    for i in nodes_list:
        if abs(1-sum(x[i][ii] for ii in total_elements)) <= 0.005:
            #print("x check", i, "OK")
            #checks_x = checks_store[0]
            checks_x[i] = checks_store[0]
        else:
            #print("x check", i, "FAIL")
            checks_x[i] = checks_store[1]
    print("\n\n")

    
    # ENERGY BALANCE
    Hreaction_digestion = ((1-x["Src1Bioreactor"]['Wa']*Aux_1)/(MWDry_CS*1E-3))*dH_c["Cattle_slurry"] - fc["BioreactorSink1"]["CH4"]*dH_c["CH4"]/(MW["CH4"]*1E-3)
    -fc["BioreactorSink1"]["H2S"]*dH_c["H2S"]/(MW["H2S"]*1E-3)
    -fc["BioreactorSink1"]["NH3"]*dH_c["NH3"]/(MW["NH3"]*1E-3)
    -(sum(fc["BioreactorSink1"][i] for i in total_elements)-fc["BioreactorSink2"]["Wa"])*dH_cD/(MWDry_D*1E-3)
    
    Q_digestor = Hreaction_digestion+(Aux_1)*c_p_liq_sol["Wa"]*(T["BioreactorSink1"]-T_amb)
    
    
    #COSTS
    AD_costs = AD_cost_module(N_animals)
    investment_cost = AD_costs['investment_cost']
    operation_cost_2016_amortized = AD_costs['operation_cost_2016_amortized']
    operation_cost_2016_non_amortized = AD_costs['operation_cost_2016_non_amortized']
    
    #CARBON EFFICIENCY
    carbon_efficiency = ((fc["BioreactorSink1"]['CH4']/MW['CH4'] + fc["BioreactorSink1"]['CO2']/MW['CO2'])*MW['C'])/fc["Src1Bioreactor"]['C'] #17.86E-03
   
    

    return {'tech':'Anaerobic digestion', 
    #'benefits':benefits_filter_result, 
    'investment_cost':investment_cost, 
    'operation_cost_2016_amortized':operation_cost_2016_amortized,
    'operation_cost_2016_non_amortized':operation_cost_2016_non_amortized,
    'fc':fc,
    'x':x,
    'F':F,
    'check_F':checks_F,
    'checks_x':checks_x,
    'carbon_efficiency':carbon_efficiency,
    }
