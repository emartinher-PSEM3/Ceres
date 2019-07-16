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

pd.options.display.max_columns = 50

#F_ini=1
def CSTR_module(F_ini,fc_ini,x_ini):
    
    # IMPORT MODULES
    from global_parameters_module import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref, density, latent_heat_evap, nat_gas_heat_value
    from feedstock_input_module import elements_wet, elements_dry, nutrients, feedstock_parameters, elements_dry_comp
    from labour_cost_module import labour_cost_module
    from equipment_costs.CSTR_cost_module import CSTR_investment_cost
    from equipment_costs.BeltFilt_design_cost import BeltFilt_design_cost
    from equipment_costs.ConveyorDryer_design_cost import ConveyorDryer_design_cost
    from equipment_costs.vessel_design_cost import vessel_design_cost
    from economic_parameters_module import ec_param
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================   
    # SETS, PARAMETERS AND NODES DATA ACQUISITION
    #nodes_matrix            = pd.read_csv('nodes/nodes_CSTR.csv', sep=",", header=None)
    #process_elements_matrix = pd.read_csv('process_elements/process_elements_CSTR.csv', sep=",", header=0)
    nodes_matrix            = pd.read_csv('cereslibrary/techmodels/nodes/nodes_CSTR_v4.csv', sep=",", header=None)
    nodes       = np.array(nodes_matrix[0].dropna())   
    process_elements_matrix = pd.read_csv('cereslibrary/techmodels/process_elements/process_elements_CSTR.csv', sep=",", header=0)
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================    
    # MANURE DATA ACQUISITION AND COMPOSITION SETTLEMENT   
    chemicals_comp   = np.array(process_elements_matrix["Component"][3:7].dropna())
    chemicals_conc   = np.full((len(chemicals_comp)), 0)
    chemicals        = dict(zip(chemicals_comp, chemicals_conc))
    
    products_comp    = np.array(process_elements_matrix["Component"][0:3].dropna())
    product_conc     = np.full((len(products_comp)), 0)
    product          = dict(zip(products_comp, product_conc))
    
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================   
    # TOTAL ELEMENTS
    total_elements = {**elements_wet,**chemicals,**product} # Merge the two dictionaries
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================   
    # General design data
#    Fm_prec                 = 2.1 #for SS 316. Walas vessel cost estimation material coefficient (SS 316)
#    max_size_centrifuge     = 49.21 # in Centrifuge max size (in) (Perry, pag 18-136)
    
    #Specefic process parameters
    Mg_P_ratio      = 2 # Mg/P molar ratio. MgCl2 dose. S Bhuiyan, M. I. H., Mavinic, D. S. and Koch, F. A. Phosphorus recovery from wastewater through struvite formation in fluidized bed reactors: a sustainable approach. Water Science and Technology, 57.2, 175-181, 2008. http://dx.doi.org/ 10.2166/wst.2008.002
    humidity_CSTR        = 1-0.2693 # %mass Struvite humidity in the moment of leave the reactor (%mass) 10.2166/wst.2014.236
    humidity_BeltFilt        = 0.5 # %mass Struvite humidity out belt filter (%mass) Walas 2012
    fines_struvite  = 0 #Struvite fines (% in mass of struvite formed)
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================
    # VARIABLES DEFINITION (IN NESTED DICTIONARIES) (INITIALIZATION)
    nodes_list              = nodes.tolist()
    initialization_comp     = total_elements
    initialization_nan      = np.full((len(initialization_comp)), 0)
    
    fc = {key: dict(zip(initialization_comp,initialization_nan)) for key in nodes_list}
    
    x = {key: dict(zip(initialization_comp,initialization_nan)) for key in nodes_list}
    
    F = {key: np.nan for key in nodes_list}
    
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================
    # MASS BALANCE
    for i in total_elements.keys():
        #x["Src1CSTR"][i]  = total_elements[i]/100
        #fc["Src1CSTR"][i] = x["Src1CSTR"][i]*F_ini
        x["Src1CSTR"][i]  = x_ini[i]
        fc["Src1CSTR"][i] = fc_ini[i]
        
    fc["Src2CSTR"]["MgCl2"]         = (fc["Src1CSTR"]["P-PO4"]/MW["P"])*Mg_P_ratio*MW["MgCl2"]
    
    #fc["ClarifBeltFilt"]["Struvite"]   = (fc["Src1CSTR"]["P-PO4"]*yield_nutrients*(1-(fines_struvite/100)))/MW["P"]*MW["Struvite"]
    #Total suspended solids penalization in precipitates formation
    DM_Src1CSTR_percentage      = 100*(fc["Src1CSTR"]["P"]+fc["Src1CSTR"]["N"]+fc["Src1CSTR"]["C"]+fc["Src1CSTR"]["Rest"]+fc["Src1CSTR"]["Ca"]+fc["Src1CSTR"]["K"])/sum(fc["Src1CSTR"][ii] for ii in total_elements)
    TSS_Src1CSTR_percentage     = 0.078*DM_Src1CSTR_percentage + 0.051
    if TSS_Src1CSTR_percentage <= 0.215:
        penalization_index = 1
    else:
        penalization_index = -7.335E-01*TSS_Src1CSTR_percentage + 1.158
    #penalization_index=1
            
    # Calcium correlations
    Ca_PO4_ratio=(fc["Src1CSTR"]["Ca_ion"]/MW["Ca"])/(fc["Src1CSTR"]["P-PO4"]/MW["PO4"])
    fc["CSTRClarif"]["Struvite"]   = penalization_index*(fc["Src1CSTR"]["P-PO4"]*(1-(fines_struvite/100)))*(0.798/(1+(Ca_PO4_ratio*0.576)**2.113))/MW['P']*MW['Struvite']
    fc["CSTRClarif"]["CaCO3"]      = penalization_index*(fc["Src1CSTR"]["Ca_ion"])*(1.020/(1+((Ca_PO4_ratio)*4.097E-01)**(1.029)))/MW['Ca']*MW['CaCO3']
    fc["CSTRClarif"]["HAP"]        = penalization_index*(fc["Src1CSTR"]["Ca_ion"])*(-4.321E-02*Ca_PO4_ratio*Ca_PO4_ratio + 3.128E-01*Ca_PO4_ratio - 3.619E-02)/MW['Ca']/5*MW['HAP']
    
    fc["CSTRClarif"]["Rest"]   = fc["Src1CSTR"]["Rest"]
    fc["CSTRClarif"]["C"]      = fc["Src1CSTR"]["C"]
    fc["CSTRClarif"]["N"]      = fc["Src1CSTR"]["N"]
    fc["CSTRClarif"]["P"]      = fc["Src1CSTR"]["P"]
    fc["CSTRClarif"]["Ca"]     = fc["Src1CSTR"]["Ca"]
    fc["CSTRClarif"]["K"]      = fc["Src1CSTR"]["K"]
    fc["CSTRClarif"]["Wa"]     = fc["Src1CSTR"]["Wa"]
    
    fc["ClarifBeltFilt"]["Struvite"]   = fc["CSTRClarif"]["Struvite"]
    fc["ClarifBeltFilt"]["CaCO3"]      = fc["CSTRClarif"]["CaCO3"]
    fc["ClarifBeltFilt"]["HAP"]        = fc["CSTRClarif"]["HAP"]
    fc["ClarifBeltFilt"]["Rest"]    = fc["CSTRClarif"]["Rest"]
    fc["ClarifBeltFilt"]["C"]      = fc["CSTRClarif"]["C"]
    fc["ClarifBeltFilt"]["N"]      = fc["CSTRClarif"]["N"]
    fc["ClarifBeltFilt"]["P"]      = fc["CSTRClarif"]["P"]
    fc["ClarifBeltFilt"]["Ca"]     = fc["CSTRClarif"]["Ca"]
    fc["ClarifBeltFilt"]["K"]      = fc["CSTRClarif"]["K"]
    
    
    
    fc["ClarifBeltFilt"]["Wa"]     = (fc["ClarifBeltFilt"]["Struvite"]+fc["ClarifBeltFilt"]["HAP"]+fc["ClarifBeltFilt"]["CaCO3"]+fc["ClarifBeltFilt"]["Rest"]+fc["ClarifBeltFilt"]["C"]+fc["ClarifBeltFilt"]["P"] +fc["ClarifBeltFilt"]["N"]+fc["ClarifBeltFilt"]["Ca"]+fc["ClarifBeltFilt"]["K"] )*humidity_CSTR/(1-humidity_CSTR)
    
    fc["ClarifSink4"]["Wa"]        = fc["Src1CSTR"]["Wa"] - fc["ClarifBeltFilt"]["Wa"] 
    if fc["ClarifSink4"]["Wa"]  >= 0:
        pass
    else:
        print('ERROR negative fc["ClarifSink4"]["Wa"]  variable')
        
    Relative_water_CSTR                   = fc["ClarifSink4"]["Wa"]/fc["Src1CSTR"]["Wa"]
    
    # ClarifSink4
    fc["ClarifSink4"]["P-PO4"]    = Relative_water_CSTR*(fc["Src1CSTR"]["P-PO4"]/MW['P']-fc["ClarifBeltFilt"]["Struvite"]/MW['Struvite']-3*fc["ClarifBeltFilt"]["HAP"]/MW['HAP'])*MW['P']
    if fc["ClarifSink4"]["P-PO4"] > 0:
        pass
    else:
        print('ERROR negative fc["ClarifSink4"]["P-PO4"] variable')
    fc["ClarifSink4"]["N-NH3"]    = Relative_water_CSTR*(fc["Src1CSTR"]["N-NH3"]/MW['N']-fc["ClarifBeltFilt"]["Struvite"]/MW['Struvite'])*MW['N']
    if fc["ClarifSink4"]["N-NH3"] > 0:
        pass
    else:
        print('ERROR negative fc["ClarifSink4"]["N-NH3"] variable')
    fc["ClarifSink4"]["Mg"]    = Relative_water_CSTR*(fc["Src2CSTR"]["MgCl2"]/MW['MgCl2']-fc["ClarifBeltFilt"]["Struvite"]/MW['Struvite'])*MW['Mg']
    if fc["ClarifSink4"]["Mg"]> 0:
        pass
    else:
        print('ERROR negative fc["ClarifSink4"]["Mg"] variable')
        
    fc["ClarifSink4"]["Cl"]     = Relative_water_CSTR*(fc["Src2CSTR"]["MgCl2"]/MW["MgCl2"])*2*MW["Cl"]
    fc["ClarifSink4"]["K_ion"]  = Relative_water_CSTR*fc["Src1CSTR"]["K_ion"]
    fc["ClarifSink4"]["Ca_ion"] = Relative_water_CSTR*(fc["Src1CSTR"]["Ca_ion"]/MW['Ca']-fc["ClarifBeltFilt"]["CaCO3"]/MW['CaCO3']-5*fc["ClarifBeltFilt"]["HAP"]/MW['HAP'])*MW['Ca']
    if fc["ClarifSink4"]["Ca_ion"] >= 0:
        pass
    else:
        print('ERROR negative fc["ClarifSink4"]["Ca_ion"] variable')
        
    # ClarifBeltFilt
    fc["ClarifBeltFilt"]["P-PO4"]    = (fc["Src1CSTR"]["P-PO4"]/MW['P']-fc["ClarifBeltFilt"]["Struvite"]/MW['Struvite']-3*fc["ClarifBeltFilt"]["HAP"]/MW['HAP'])*MW['P']-fc["ClarifSink4"]["P-PO4"]
    if fc["ClarifBeltFilt"]["P-PO4"] > 0:
        pass
    else:
        print('ERROR negative fc["ClarifBeltFilt"]["P-PO4"] variable')
        
    fc["ClarifBeltFilt"]["N-NH3"]    = fc["Src1CSTR"]["N-NH3"] -fc["ClarifSink4"]["N-NH3"] 
    if fc["ClarifBeltFilt"]["N-NH3"] > 0:
        pass
    else:
        print('ERROR negative fc["ClarifBeltFilt"]["N-NH3"] variable')
        
    fc["ClarifBeltFilt"]["Mg"]    = (fc["Src2CSTR"]["MgCl2"]/MW['MgCl2']-fc["ClarifBeltFilt"]["Struvite"]/MW['Struvite'])*MW['Mg'] - fc["ClarifSink4"]["Mg"] 
    if fc["ClarifBeltFilt"]["Mg"]> 0:
        pass
    else:
        print('ERROR negative fc["ClarifBeltFilt"]["Mg"] variable')
        
    fc["ClarifBeltFilt"]["Cl"]     = (fc["Src2CSTR"]["MgCl2"]/MW["MgCl2"])*2*MW["Cl"] -fc["ClarifSink4"]["Cl"]
    fc["ClarifBeltFilt"]["K_ion"]  = fc["Src1CSTR"]["K_ion"] - fc["ClarifSink4"]["K_ion"] 
    fc["ClarifBeltFilt"]["Ca_ion"] = fc["Src1CSTR"]["Ca_ion"] - fc["ClarifSink4"]["Ca_ion"]
    if fc["ClarifBeltFilt"]["Ca_ion"] >= 0:
        pass
    else:
        print('ERROR negative fc["ClarifBeltFilt"]["Ca_ion"] variable')
        
    
    
    
    # The humidity in the cake is calculated on the basis of mass of struvite and TS (it is considered that the cake is formed by struvite and TS)
    fc["BeltFiltDryer"]["Struvite"]  = fc["ClarifBeltFilt"]["Struvite"]
    fc["BeltFiltDryer"]["HAP"]       = fc["ClarifBeltFilt"]["HAP"]
    fc["BeltFiltDryer"]["CaCO3"]     = fc["ClarifBeltFilt"]["CaCO3"]
    fc["BeltFiltDryer"]["Rest"]      = fc["ClarifBeltFilt"]["Rest"]
    fc["BeltFiltDryer"]["C"]         = fc["ClarifBeltFilt"]["C"]
    fc["BeltFiltDryer"]["P"]         = fc["ClarifBeltFilt"]["P"]
    fc["BeltFiltDryer"]["N"]         = fc["ClarifBeltFilt"]["N"]
    fc["BeltFiltDryer"]["Ca"]        = fc["ClarifBeltFilt"]["Ca"]
    fc["BeltFiltDryer"]["K"]         = fc["ClarifBeltFilt"]["K"]
    #iT IS CONSIDER WATER IS COMPLETELY SEPARATED (PERRY PAGE 12-66 (APPROXIMATED AS CALCIUM CARBONATE))
    fc["BeltFiltDryer"]["Wa"]        = (fc["BeltFiltDryer"]["Struvite"]+fc["ClarifBeltFilt"]["HAP"]+fc["ClarifBeltFilt"]["CaCO3"]+fc["BeltFiltDryer"]["Rest"]+fc["BeltFiltDryer"]["C"]+fc["BeltFiltDryer"]["P"] +fc["BeltFiltDryer"]["N"]+fc["BeltFiltDryer"]["Ca"]+fc["BeltFiltDryer"]["K"] )*humidity_BeltFilt/(1-humidity_BeltFilt)
    #fc["BeltFiltDryer"]["Wa"]        = sum(fc["BeltFiltDryer"][ii] for ii in total_elements if ii!="Wa")*humidity_BeltFilt/(1-humidity_BeltFilt) 
    fc["BeltFiltSink1"]["Wa"]        = fc["ClarifBeltFilt"]["Wa"]-fc["BeltFiltDryer"]["Wa"]
    if fc["BeltFiltSink1"]["Wa"]  > 0:
        pass
    else:
        print('ERROR negative fc["BeltFiltSink1"]["Wa"] variable')
    
    Relative_water_BeltFilt          = fc["BeltFiltSink1"]["Wa"]/fc["ClarifBeltFilt"]["Wa"]
    fc["BeltFiltSink1"]["P-PO4"]     = fc["ClarifBeltFilt"]["P-PO4"]*Relative_water_BeltFilt
    fc["BeltFiltSink1"]["N-NH3"]     = fc["ClarifBeltFilt"]["N-NH3"]*Relative_water_BeltFilt
    fc["BeltFiltSink1"]["Mg"]        = fc["ClarifBeltFilt"]["Mg"]*Relative_water_BeltFilt
    fc["BeltFiltSink1"]["Cl"]        = fc["ClarifBeltFilt"]["Cl"]*Relative_water_BeltFilt
    #fc["BeltFiltSink1"]["K"]         = fc["ClarifBeltFilt"]["K"]*Relative_water
    #fc["BeltFiltSink1"]["N"]         = fc["ClarifBeltFilt"]["N"]*Relative_water
    #fc["BeltFiltSink1"]["P"]         = fc["ClarifBeltFilt"]["P"]*Relative_water
    #fc["BeltFiltSink1"]["Ca"]        = fc["ClarifBeltFilt"]["Ca"]*Relative_water
    fc["BeltFiltSink1"]["Ca_ion"]    = fc["ClarifBeltFilt"]["Ca_ion"]*Relative_water_BeltFilt
    fc["BeltFiltSink1"]["K_ion"]     = fc["ClarifBeltFilt"]["K_ion"]*Relative_water_BeltFilt
    
    fc["BeltFiltDryer"]["P-PO4"]       = fc["ClarifBeltFilt"]["P-PO4"]-fc["BeltFiltSink1"]["P-PO4"]
    fc["BeltFiltDryer"]["N-NH3"]       = fc["ClarifBeltFilt"]["N-NH3"]-fc["BeltFiltSink1"]["N-NH3"]
    fc["BeltFiltDryer"]["Mg"]        = fc["ClarifBeltFilt"]["Mg"]-fc["BeltFiltSink1"]["Mg"]
    fc["BeltFiltDryer"]["Cl"]        = fc["ClarifBeltFilt"]["Cl"]-fc["BeltFiltSink1"]["Cl"]
    #fc["BeltFiltDryer"]["K"]         = fc["ClarifBeltFilt"]["K"]-fc["BeltFiltSink1"]["K"]
    #fc["BeltFiltDryer"]["N"]         = fc["ClarifBeltFilt"]["N"]-fc["BeltFiltSink1"]["N"]
    #fc["BeltFiltDryer"]["P"]         = fc["ClarifBeltFilt"]["P"]-fc["BeltFiltSink1"]["P"]
    #fc["BeltFiltDryer"]["Ca"]        = fc["ClarifBeltFilt"]["Ca"]-fc["BeltFiltSink1"]["Ca"]
    fc["BeltFiltDryer"]["Ca_ion"]    = fc["ClarifBeltFilt"]["Ca_ion"]-fc["BeltFiltSink1"]["Ca_ion"]
    fc["BeltFiltDryer"]["K_ion"]     = fc["ClarifBeltFilt"]["K_ion"]-fc["BeltFiltSink1"]["K_ion"]
    
    fc["DryerSink2"]["Wa"]          = fc["BeltFiltDryer"]["Wa"] 
    
    fc["DryerSink3"]["Struvite"]  = fc["BeltFiltDryer"]["Struvite"]
    fc["DryerSink3"]["HAP"]       = fc["BeltFiltDryer"]["HAP"]
    fc["DryerSink3"]["CaCO3"]     = fc["BeltFiltDryer"]["CaCO3"]
    fc["DryerSink3"]["Rest"]      = fc["BeltFiltDryer"]["Rest"]
    fc["DryerSink3"]["C"]         = fc["BeltFiltDryer"]["C"]
    fc["DryerSink3"]["P"]         = fc["BeltFiltDryer"]["P"]
    fc["DryerSink3"]["N"]         = fc["BeltFiltDryer"]["N"]
    fc["DryerSink3"]["Ca"]        = fc["BeltFiltDryer"]["Ca"]
    fc["DryerSink3"]["K"]         = fc["BeltFiltDryer"]["K"]
    fc["DryerSink3"]["P-PO4"]     = fc["BeltFiltDryer"]["P-PO4"]
    fc["DryerSink3"]["N-NH3"]     = fc["BeltFiltDryer"]["N-NH3"]
    fc["DryerSink3"]["Mg"]        = fc["BeltFiltDryer"]["Mg"]
    fc["DryerSink3"]["Cl"]        = fc["BeltFiltDryer"]["Cl"]
    fc["DryerSink3"]["Ca_ion"]    = fc["BeltFiltDryer"]["Ca_ion"]
    fc["DryerSink3"]["K_ion"]     = fc["BeltFiltDryer"]["K_ion"]
    
    Struvite_fines = (fc["DryerSink3"]["Struvite"]/(1-(fines_struvite/100)))*(fines_struvite/100)
    Struvite_recovered = fc["DryerSink3"]["Struvite"]+fc["DryerSink3"]["HAP"]+Struvite_fines
    
    for i in nodes_list:
        F[i] = sum(fc[i][ii] for ii in total_elements)
        
    for i in nodes_list:
        if i!="Src1CSTR":
            for ii in total_elements.keys():
                x[i][ii] = fc[i][ii]/F[i]
    
    #    Checks
    checks_store = ['OK', 'FAIL']
    checks_F = []
    checks_x = []

#    for i in total_elements.keys():
#        if abs(fc["BeltFiltSink1"][i] + fc["DryerSink2"][i] + fc["DryerSink3"][i] - (fc["Src1CSTR"][i]+fc["Src2CSTR"][i])) <= 0.005:
#            print("fc check", i, "OK")
#        else:
#            print("fc check", i, "FAIL")
    
    if abs(F["BeltFiltSink1"] + F["DryerSink2"] + F["DryerSink3"] + F["ClarifSink4"] - (F["Src1CSTR"]+F["Src2CSTR"])) <= 0.005:
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
    #pH adjust
    pH_ini=feedstock_parameters['pH']
    pOH_ini=14 - pH_ini
    conc_OH_molar_ini = 10**(-pOH_ini)
    
    pH_fin=9
    pOH_fin=14 - pH_fin
    conc_OH_molar_fin = 10**(-pOH_fin)
    
    delta_conc_OH_molar = conc_OH_molar_fin - conc_OH_molar_ini
    
    NaOH_molar = delta_conc_OH_molar
    
    NaOH_kg = NaOH_molar*MW['NaOH']*F_ini/(feedstock_parameters['digestate_density']*1000)*3600*24*365 #kg/year
          
            
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================   
    # ECONOMICS/DESIGN
    #-------------------------Residence time----------------------------------
    #Struvite formation
    K_ps            = 7.08E-14 # solubility product doi:10.1016/S0960-8524(03)00076-2
    k               = 12.3/3600 #s-1 reaction kinetic constant 1st order. Struvite precipitation in anaerobic swine lagoon liquid: effect of pH and Mg:P ratio and determination of rate constant . Nelson et al, 2003
    G               = 1E-2*1E-6 # m/s 10.1007/s11696-018-0613-5 Induction time is negigible (10.1016/j.watres.2013.03.007)
    L_crystal       = 40E-6 # m 10.1007/s11696-018-0613-5    10.1016/j.cej.2012.10.038
    
    
    NH4_molar               = ((fc["Src1CSTR"]["N-NH3"])/MW["N"])/((F_ini/feedstock_parameters['digestate_density'])*UnitConv['L_to_m3'])
    Mg_molar                = ((fc["Src2CSTR"]["MgCl2"])/MW["MgCl2"])/((F_ini/feedstock_parameters['digestate_density'])*UnitConv['L_to_m3'])
    PO4_molar               = ((fc["Src1CSTR"]["P-PO4"])/MW["P"])/((F_ini/feedstock_parameters['digestate_density'])*UnitConv['L_to_m3'])
    PO4_molar_equilibrium   = K_ps/(NH4_molar*Mg_molar)
    reaction_time          =(np.log((PO4_molar*(1-(fc["ClarifBeltFilt"]["P-PO4"]/fc["Src1CSTR"]["P-PO4"] )))-PO4_molar_equilibrium)-np.log(PO4_molar-PO4_molar_equilibrium))/(-k) #(s)
    
    growth_time             = L_crystal/G
    total_time              = reaction_time+growth_time
    
    #-------------------------CSTR cost----------------------------------
    mixing_operation='Slurries' #Operation types: 'Blending','Homogeneous reaction','Reaction with heat transfer','Liquid-liquid mixtures','Liquid-gas mixtures','Slurries'
    CSTR_results = CSTR_investment_cost (F_ini, total_time, mixing_operation)
    
    CSTR_V = CSTR_results['reactor_V']
    CSTR_D = CSTR_results['reactor_D']
    CSTR_L = CSTR_results['reactor_L']
    agitator_power = CSTR_results['agitator_power']
    n_CSTR = CSTR_results['n_reactors']
    CSTR_cost_2016 = CSTR_results['CSTR_cost_2016']
    CSTR_operation_cost_2016 = CSTR_results['CSTR_operation_cost_2016']
    
    
    #-------------------------Clarifier----------------------------------
    HRT = 3600 #s
    Clarifier_results = vessel_design_cost(F["CSTRClarif"], HRT)
    
    Clarifier_V_total = Clarifier_results['Volume']
    #Results
    Clarifier_V = Clarifier_results['V_design']
    Clarifier_D = Clarifier_results['D_design']
    Clarifier_L = Clarifier_results['L_design']
    n_Clarifier = Clarifier_results['n_vessels']
    Clarifier_cost_2016 =  Clarifier_results['vessels_cost_2016']
    
    #--------------------------------Centrifuge-------------------------------------
    #        Centrifuge size (in). Mass flow must be in ton/h. (Perry, pag 18-136), Type: Pusher centrifuge, max size 1250 mm
    #Centrifuge_size = 0.3308*(F["ClarifBeltFilt"]/1000*3600)+9.5092
    #n_centrif = np.ceil(Centrifuge_size/max_size_centrifuge)
    #Centrifuge_design_size = min(max_size_centrifuge,Centrifuge_size)
    #Centrifuge_cost_2004 = (10272*Centrifuge_design_size-24512)*n_centrif
    #Centrifuge_cost_2016 = Centrifuge_cost_2004*(CEI[2016]/CEI[2004])
    
    #--------------------------------Belt Filt-------------------------------------
    BeltFilt_results = BeltFilt_design_cost (fc["BeltFiltSink1"]["Wa"])
    BeltFilt_area = BeltFilt_results['Area']
    n_BeltFilt = BeltFilt_results['n_filt']
    BeltFilt_cost_2016 = BeltFilt_results['BeltFilt_cost_2016']
    
    #--------------------------------HX-------------------------------------
    #T_in_hot = 100+373 #K
    #T_out_hot = 100+273 #K
    #T_in_cold = 298 #K
    #T_out_cold = 298 #K
    #deltaT = ((T_in_hot-T_out_cold)-(T_out_hot-T_in_cold))/np.log((T_in_hot-T_out_cold)/(T_out_hot-T_in_cold))
    #
    ##Q=m_H2O*lambda
    #lambda_Wa = 2264 # (kJ/kg)
    #Q_latent = fc["BeltFiltDryer"]["Wa"]*lambda_Wa
    #
    #h_hot_stream = 0.028
    #h_cold_stream = 0.85
    #U = (1/h_hot_stream+1/h_cold_stream)**(-1)
    #A = Q_latent/(U*deltaT) #
    #
    #n_HX = np.ceil(A/2000)
    #
    #HX_cost = n_HX*20044*(A/n_HX)**0.47
    
    #--------------------------------Dryer-------------------------------------
    ConveyorDryer_results = ConveyorDryer_design_cost (F['BeltFiltDryer'], fc["BeltFiltDryer"]["Wa"])
    ConveyorDryer_area = ConveyorDryer_results['Area']
    n_ConveyorDryer = ConveyorDryer_results['n_dryer']
    ConveyorDryer_cost_2016 = ConveyorDryer_results['ConveyorDryer_cost_2016']
    ConveyorDryer_operating_cost_2016 = ConveyorDryer_results['ConveyorDryer_operating_cost_2016']
    
    
    # OPERATION  
    
    equipment_cost              = (CSTR_cost_2016+ Clarifier_cost_2016 + BeltFilt_cost_2016 + ConveyorDryer_cost_2016)
    physical_plant_cost_2016    = 3.15*equipment_cost
    fixed_capital_cost_2016     = 1.4*physical_plant_cost_2016
    
    chemicals_cost_2016 = price["MgCl2"]*fc["Src2CSTR"]["MgCl2"]*3600*24*365 + NaOH_kg*price["NaOH"]
    N_solids_steps  = 1
    N_compressors   = 0
    N_towers        = 0
    N_reactors      = 1
    N_heaters       = 1
    N_exchangers    = 0
    labor_cost_2016    = labour_cost_module(N_solids_steps, N_compressors, N_towers, N_reactors, N_heaters, N_exchangers)
    #operation_cost_2016 = (chemicals_cost_2016 + 0.3*fixed_capital_cost_2016) + 1.5*labor_cost_2016['labor_cost'])+CSTR_operation_cost_2016+ConveyorDryer_operating_cost_2016
    operation_cost_2016_amortized = (chemicals_cost_2016 + (fixed_capital_cost_2016/ec_param['plant_lifetime']))+CSTR_operation_cost_2016+ConveyorDryer_operating_cost_2016 #+ 1.5*labor_cost_2016['labor_cost']
    operation_cost_2016_non_amortized = (chemicals_cost_2016)+CSTR_operation_cost_2016+ConveyorDryer_operating_cost_2016 #+ 1.5*labor_cost_2016['labor_cost']
    
    Struvite_benefits = Struvite_recovered*3600*24*334*price["struvite"]
            
    #Benefits = Struvite_benefits-operation_cost_2016
    
    recovered_P = fc["DryerSink3"]["P"]
    recovered_PO4 = fc["DryerSink3"]["Struvite"]/MW['Struvite']*MW['P']+3*fc["DryerSink3"]["HAP"]/MW['HAP']*MW['P']
    released_P = fc["BeltFiltSink1"]["P"]+fc["ClarifSink4"]["P"]
    released_PO4 = fc["BeltFiltSink1"]["P-PO4"]+fc["ClarifSink4"]["P-PO4"]+fc["DryerSink3"]["P-PO4"]
    
    fraction_recoved_P = recovered_P/(fc["Src1CSTR"]["P"])
    fraction_recoved_PO4 = recovered_PO4/fc["Src1CSTR"]["P-PO4"]
    fraction_recoved_TP = (recovered_P+recovered_PO4)/(fc["Src1CSTR"]["P"]+fc["Src1CSTR"]["P-PO4"])
    fraction_released_P = released_P/(fc["Src1CSTR"]["P"])
    fraction_released_PO4 = released_PO4/(fc["Src1CSTR"]["P-PO4"])
    fraction_released_TP = (released_P+released_PO4)/(fc["Src1CSTR"]["P"]+fc["Src1CSTR"]["P-PO4"])
    
    PO4_conc_released = (fc["BeltFiltSink1"]["P-PO4"]+fc["ClarifSink4"]["P-PO4"]+fc["DryerSink3"]["P-PO4"])*UnitConv['K_to_mili']/((sum(fc["BeltFiltSink1"][ii] for ii in total_elements)+sum(fc["ClarifSink4"][ii] for ii in total_elements)+sum(fc["DryerSink3"][ii] for ii in total_elements))/feedstock_parameters['Wa_density'])
        
    return {'tech':'Struvite CSTR reactor',
            'Reactor V':CSTR_V, 'Reactor D':CSTR_D, 'Reactor L':CSTR_L,'agitator_power':agitator_power,'n_CSTR':n_CSTR, 'CSTR_cost_2016':CSTR_cost_2016, 'CSTR_operation_cost_2016':CSTR_operation_cost_2016,
            'Clarifier V':Clarifier_V, 'Clarifier D':Clarifier_D, 'Clarifier L':Clarifier_L,'n_Clarifier':n_Clarifier, 'Clarifier_cost_2016':Clarifier_cost_2016,
            'BeltFilt_area':BeltFilt_area, 'n_BeltFilt':n_BeltFilt, 'BeltFilt_cost_2016':BeltFilt_cost_2016,
            'ConveyorDryer_area':ConveyorDryer_area, 'n_ConveyorDryer':n_ConveyorDryer, 'ConveyorDryer_cost_2016':ConveyorDryer_cost_2016,'ConveyorDryer_operating_cost_2016':ConveyorDryer_operating_cost_2016,
            'Struvite_benefits':Struvite_benefits,
            #'Benefits':Benefits,
            'equipment_cost':equipment_cost,
            'investment_cost':fixed_capital_cost_2016, 
            'labor_cost_2016':labor_cost_2016, 
            'operation_cost_2016_amortized':operation_cost_2016_amortized,
            'operation_cost_2016_non_amortized':operation_cost_2016_non_amortized,
            'fc':fc,
            'x':x,
            'F':F,
            'check_F':checks_F,
            'checks_x':checks_x,
            'recovered_P':recovered_P,
            'recovered_PO4':recovered_PO4,
            'released_P':released_P,
            'released_PO4':released_PO4,
            'fraction_recoved_P':fraction_recoved_P,
            'fraction_recoved_PO4':fraction_recoved_PO4,
            'fraction_released_P':fraction_released_P,
            'fraction_released_PO4':fraction_released_PO4,         
            'fraction_recoved_TP':fraction_recoved_TP,
            'fraction_released_TP':fraction_released_TP,
            'PO4_conc_released':PO4_conc_released,   
            }

    
    
 
    
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================
        
        
    # GRAPH
    
    #G=pgv.AGraph(directed=True,)
    #G.edge_attr.update(len='2.0',color='black')
    ##G.node_attr['style']='filled'
    ##nodelist=['Src1','Filter','Sink1', 'Sink2']
    ##G.add_nodes_from(nodelist, color='white')
    #G.add_node('Src1', style='filled', color='darkgoldenrod2',shape='diamond')
    #G.add_node('Src2', style='filled', color='darkgoldenrod2',shape='diamond')
    #G.add_node('PrecTank', style='filled', color='darkgoldenrod2',shape='diamond')
    #G.add_node('Centrif', style='filled', color='darkgoldenrod2',shape='diamond')
    #G.add_node('Sink1', style='filled', color='darkgoldenrod2',shape='diamond')
    #G.add_node('Sink2', style='filled', color='darkgoldenrod2',shape='diamond')
    #G.add_edge('Src1','PrecTank')
    #G.add_edge('Src2','PrecTank')
    #G.add_edge('PrecTank','Centrif')
    #G.add_edge('Centrif','Sink1')
    #G.add_edge('Centrif','Sink2')
    #
    #G.graph_attr['label']='Centrifugation'
    ##G.node_attr['shape']='circle'
    #
    ##G.string()
    #G.layout(prog='dot') 
    #G.draw('Centrifugation.png')
    #print("Centrifugation.png")



