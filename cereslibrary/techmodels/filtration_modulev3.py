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

def filtration_module(F_ini,fc_ini,x_ini):
    
    # IMPORT MODULES
    from global_parameters_module import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref, density, latent_heat_evap, nat_gas_heat_value
    from feedstock_input_module import elements_wet, elements_dry, nutrients, feedstock_parameters, elements_dry_comp
    from labour_cost_module import labour_cost_module
    from equipment_costs.gravity_pressure_filter_cost_module import filter_package_investment_cost, filter_package_operation_cost
    from economic_parameters_module import ec_param
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================
    # SETS, PARAMETERS AND NODES DATA ACQUISITION
    nodes_matrix        = pd.read_csv('cereslibrary/techmodels/nodes/nodes_filtration.csv', sep=",", header=None)
    #nodes_matrix        = pd.read_csv('nodes/nodes_filtration.csv', sep=",", header=None)
    nodes       = np.array(nodes_matrix[0].dropna())   
    
    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================  
    # TOTAL ELEMENTS
    total_elements = elements_wet

    # ===============================================================================================================================================================================================================================
    # ###############################################################################################################################################################################################################################
    # ===============================================================================================================================================================================================================================
    # FILTRATION MEDIA
    filter_matrix           = pd.read_csv('cereslibrary/techmodels/equipment_parameters/Filter.csv', sep=",", header=0)
    #filter_matrix               = pd.read_csv('equipment_parameters/Filter.csv', sep=",", header=0)
    filter_media                = np.array(filter_matrix["Filtration_medium"].dropna()) #NaN removed
    filter_yieldPO4             = dict(zip(filter_media, np.array(filter_matrix["PO4"].dropna())))
    filter_yieldNH4             = dict(zip(filter_media, np.array(filter_matrix["NH4"].dropna())))
    filter_P_sepindex           = 0.77 #Organic P, Shilton et al., 2006
    filter_N_sepindex           = 0.15 #Organic P, Hjorth et al., 2010
    capacity_filter_media_PO4   = dict(zip(filter_media, np.array(filter_matrix["capacity_filter_media_PO4"].dropna())))
    filter_price                = dict(zip(filter_media, np.array(filter_matrix["filter_price"].dropna())))
    
    filter_max_capacity = 1300 #Filter max capacity ft3 per min Process Equipmetn Cost Estimation. Final Report. Loh, Lyons and White, 2002 (NETL)http://www.osti.gov/scitech/servlets/purl/797810/ Material A2895C, 1998 $ Filter type: cartridge filter
    
    
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
      
    for aa in filter_media.tolist():
        for i in total_elements.keys():
#            x["SrcFilter"][i]  = total_elements[i]/100
#            fc["SrcFilter"][i] = x["SrcFilter"][i]*F_ini
            x["SrcFilter"][i]  = x_ini[i]
            fc["SrcFilter"][i] = fc_ini[i]
                   
        fc["FilterSink2"]["P-PO4"]  = fc["SrcFilter"]["P-PO4"]*filter_yieldPO4[aa]
        fc["FilterSink2"]["N-NH3"]  = fc["SrcFilter"]["N-NH3"]*filter_yieldNH4[aa]
        fc["FilterSink2"]["Rest"]   = fc["SrcFilter"]["Rest"]
        fc["FilterSink2"]["C"]      = fc["SrcFilter"]["C"]
        fc["FilterSink2"]["Ca"]     = fc["SrcFilter"]["Ca"]
        fc["FilterSink2"]["K"]      = fc["SrcFilter"]["K"]
        fc["FilterSink2"]["P"]      = fc["SrcFilter"]["P"]*filter_P_sepindex
        fc["FilterSink2"]["N"]      = fc["SrcFilter"]["N"]*filter_N_sepindex
        fc["FilterSink2"]["Wa"]     = (0.15/0.85)*sum(fc["FilterSink2"][i] for i in elements_dry)
        
        for i in elements_wet.keys():
            fc["FilterSink1"][i] = fc["SrcFilter"][i]-fc["FilterSink2"][i]
        
        for i in nodes_list:
            F[i] = sum(fc[i][ii] for ii in total_elements)
            
        for i in nodes_list:
            if i!="SrcFilter":
                for ii in elements_wet.keys():
                    x[i][ii] = fc[i][ii]/F[i]
        
            
#        Checks
#        print('Filter media: ', aa)
        checks_store = ['OK', 'FAIL']
        checks_F = []
        checks_x = []
#        for i in total_elements.keys():
#            if abs(fc["FilterSink2"][i] + fc["FilterSink1"][i] - fc["SrcFilter"][i]) <= 0.005:
#                print("fc check", i, "OK")
#            else:
#                print("fc check", i, "FAIL")
#        
        if abs(F["FilterSink2"] + F["FilterSink1"] - F["SrcFilter"]) <= 0.005:
#            print("F check OK")
            checks_F = checks_store[0]
        else:
#            print("F check FAIL")
            checks_F = checks_store[1]
            
        
        for i in nodes_list:
            if abs(1-sum(x[i][ii] for ii in total_elements)) <= 0.005:
#                print("x check", i, "OK")
                checks_x = checks_store[0]
            else:
#                print("x check", i, "FAIL")
                checks_x = checks_store[1]
        print("\n\n")
                
                
        # ===============================================================================================================================================================================================================================
        # ###############################################################################################################################################################################################################################
        # ===============================================================================================================================================================================================================================
        # ECONOMICS/DESIGN FILTER
        
        # INVESTMENT                       
        economics_design_filter_investment = filter_package_investment_cost(F["SrcFilter"]*3600/feedstock_parameters['digestate_density']*UnitConv['L_to_m3'])
        filter_type =  economics_design_filter_investment['filter_type']
        n_filters = economics_design_filter_investment['n_filters']
        filter_cost_2016_USD = economics_design_filter_investment['filter_package_investment_cost_2016_USD']
        investment_cost_status = economics_design_filter_investment['status']
            
#        Lifetime: 1 year
        filter_medium_cost = ((fc["SrcFilter"]["P-PO4"]*3600*24*365)/capacity_filter_media_PO4[aa])*filter_price[aa] 

        total_filter_investment_cost = filter_cost_2016_USD+filter_medium_cost
        
        # OPERATION                
        economics_design_filter_operation = filter_package_operation_cost(F["SrcFilter"]*3600/feedstock_parameters['digestate_density']*UnitConv['L_to_m3'])
        filter_operational_cost_2016_USD = economics_design_filter_operation['filter_package_operation_cost_2016_USD']
        operation_cost_status = economics_design_filter_operation['status']

        
        
#        N_solids_steps  = 1
#        N_compressors   = 0
#        N_towers        = 0
#        N_reactors      = 0
#        N_heaters       = 0
#        N_exchangers    = 0
#        
#        labour_cost = labour_cost_module(N_solids_steps, N_compressors, N_towers, N_reactors, N_heaters, N_exchangers)
        
#       Labor cost included in operaitonal cost (EPA estimation)        
        total_filter_operational_cost = filter_operational_cost_2016_USD 
        
        Investment_cost_filter = total_filter_investment_cost
        #Operational_cost_filter = total_filter_operational_cost + 0.3*Investment_cost_filter
        operation_cost_2016_amortized = (total_filter_operational_cost + (Investment_cost_filter/ec_param['plant_lifetime']))
        operation_cost_2016_non_amortized = total_filter_operational_cost
        Benefits_filter = 0-operation_cost_2016_amortized
        
        
        filter_media_store =[]
        benefits_filter_store = []
        investment_cost_filter_store = []
        operation_cost_2016_amortized_filter_store = []
        operation_cost_2016_non_amortized_filter_store = []
        filter_type_store = []
        n_filters_store = []
        investment_cost_status_store = []
        operation_cost_status_store = []
        checks_F_store = []
        checks_x_store = []
        recoved_P_store = []
        recoved_PO4_store = []
        released_P_store = []
        released_PO4_store = []
        fraction_recoved_P_store = []
        fraction_recoved_PO4_store = []
        fraction_released_P_store = []
        fraction_released_PO4_store = []
        fraction_recoved_TP_store = []
        fraction_released_TP_store = []
        PO4_conc_released_store = []
        
        
        filter_media_store.append(aa)
        filter_type_store.append(filter_type)
        n_filters_store.append(n_filters)
        investment_cost_status_store.append(investment_cost_status)
        operation_cost_status_store.append(operation_cost_status)
        benefits_filter_store.append(Benefits_filter)
        investment_cost_filter_store.append(Investment_cost_filter)
        operation_cost_2016_amortized_filter_store.append(operation_cost_2016_amortized)
        operation_cost_2016_non_amortized_filter_store.append(operation_cost_2016_non_amortized)
        checks_F_store.append(checks_F)
        checks_x_store.append(checks_x)
        recoved_P_store.append(fc["FilterSink2"]["P"])
        recoved_PO4_store.append(fc["FilterSink2"]["P-PO4"])
        released_P_store.append(fc["FilterSink1"]["P"])
        released_PO4_store.append(fc["FilterSink1"]["P-PO4"])
        fraction_recoved_P = fc["FilterSink2"]["P"]/(fc["SrcFilter"]["P"])
        fraction_recoved_PO4 = (fc["FilterSink2"]["P-PO4"]/(fc["SrcFilter"]["P-PO4"]))
        fraction_recoved_TP = (fc["FilterSink2"]["P"]+fc["FilterSink2"]["P-PO4"])/(fc["SrcFilter"]["P"]+fc["SrcFilter"]["P-PO4"])
        fraction_released_P = fc["FilterSink1"]["P"]/(fc["SrcFilter"]["P"])
        fraction_released_PO4 = fc["FilterSink1"]["P-PO4"]/(fc["SrcFilter"]["P-PO4"])
        fraction_released_TP = (fc["FilterSink1"]["P"]+fc["FilterSink1"]["P-PO4"])/(fc["SrcFilter"]["P"]+fc["SrcFilter"]["P-PO4"])
        fraction_recoved_P_store.append(fraction_recoved_P)
        fraction_recoved_PO4_store.append(fraction_recoved_PO4)
        fraction_released_P_store.append(fraction_released_P)
        fraction_recoved_TP_store.append(fraction_recoved_TP)
        fraction_released_PO4_store.append(fraction_released_PO4)
        fraction_released_TP_store.append(fraction_released_TP)
        PO4_conc_released = fc["FilterSink1"]["P-PO4"]*UnitConv['K_to_mili']/(sum(fc["FilterSink1"][ii] for ii in total_elements)/feedstock_parameters['Wa_density'])
        PO4_conc_released_store.append(PO4_conc_released)
      
    filter_media_result = filter_media_store[benefits_filter_store.index(max(benefits_filter_store))]
    filter_type_result = filter_type_store[benefits_filter_store.index(max(benefits_filter_store))]
    n_filters_result = n_filters_store[benefits_filter_store.index(max(benefits_filter_store))]
    investment_cost_status_result = investment_cost_status_store[benefits_filter_store.index(max(benefits_filter_store))]
    operation_cost_status_result = operation_cost_status_store[benefits_filter_store.index(max(benefits_filter_store))]
    benefits_filter_result = max(benefits_filter_store)
    investment_cost_filter_result = investment_cost_filter_store[benefits_filter_store.index(max(benefits_filter_store))]
    operation_cost_2016_amortized_filter_result = operation_cost_2016_amortized_filter_store[benefits_filter_store.index(max(benefits_filter_store))]
    operation_cost_2016_non_amortized_filter_result = operation_cost_2016_non_amortized_filter_store[benefits_filter_store.index(max(benefits_filter_store))]
    checks_F_result = checks_F_store[benefits_filter_store.index(max(benefits_filter_store))]
    checks_x_result = checks_x_store[benefits_filter_store.index(max(benefits_filter_store))]
    recoved_P_result = recoved_P_store[benefits_filter_store.index(max(benefits_filter_store))]
    recoved_PO4_result = recoved_PO4_store[benefits_filter_store.index(max(benefits_filter_store))]
    released_P_result = released_P_store[benefits_filter_store.index(max(benefits_filter_store))]
    released_PO4_result = released_PO4_store[benefits_filter_store.index(max(benefits_filter_store))]
    fraction_recoved_P_result = fraction_recoved_P_store[benefits_filter_store.index(max(benefits_filter_store))]
    fraction_recoved_PO4_result = fraction_recoved_PO4_store[benefits_filter_store.index(max(benefits_filter_store))]
    fraction_released_P_result = fraction_released_P_store[benefits_filter_store.index(max(benefits_filter_store))]
    fraction_released_PO4_result = fraction_released_PO4_store[benefits_filter_store.index(max(benefits_filter_store))]
    fraction_recoved_TP_result = fraction_recoved_TP_store[benefits_filter_store.index(max(benefits_filter_store))]
    fraction_released_TP_result  = fraction_released_TP_store[benefits_filter_store.index(max(benefits_filter_store))]
    PO4_conc_released_result  = PO4_conc_released_store[benefits_filter_store.index(max(benefits_filter_store))]
    
       
    return {'tech':'Filtration',
            'filter_media':filter_media_result,
            'filter_type':filter_type_result,
            'n_filters':n_filters_result, 
            'benefits':benefits_filter_result, 
            'investment_cost':investment_cost_filter_result, 
            'operation_cost_2016_amortized':operation_cost_2016_amortized_filter_result, 
            'operation_cost_2016_non_amortized':operation_cost_2016_non_amortized_filter_result,
            'fc':fc,
            'x':x,
            'F':F,
            'check_F':checks_F_result,
            'checks_x':checks_x_result,
            'investment_cost_status':investment_cost_status_result,
            'operation_cost_status':operation_cost_status_result,
            'recoved_P':recoved_P_result,
            'recoved_PO4':recoved_PO4_result,
            'released_P':released_P_result,
            'released_PO4':released_PO4_result,
            'fraction_recoved_P':fraction_recoved_P_result,
            'fraction_recoved_PO4':fraction_recoved_PO4_result,
            'fraction_released_P':fraction_released_P_result,
            'fraction_released_PO4':fraction_released_PO4_result,
            'fraction_recoved_TP':fraction_recoved_TP_result,
            'fraction_released_TP':fraction_released_TP_result,
            'PO4_conc_released':PO4_conc_released_result,
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
#G.add_node('Filter', style='filled', color='darkgoldenrod2',shape='diamond')
#G.add_node('Sink1', style='filled', color='darkgoldenrod2',shape='diamond')
#G.add_node('Sink2', style='filled', color='darkgoldenrod2',shape='diamond')
#G.add_edge('Src1','Filter')
#G.add_edge('Filter','Sink1')
#G.add_edge('Filter','Sink2')
#
#G.graph_attr['label']='Filtration'
##G.node_attr['shape']='circle'
#
##G.string()
#G.layout(prog='dot') 
#G.draw('file.png')
#print("file.png")



