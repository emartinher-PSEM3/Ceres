import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#Pruebas
#F_total = 1
#fc_N_NH3_in=0.3
#fc_P_PO4_in=0.1
#fc_MgCl2_in=0.2
#fc_P_PO4_out=fc_P_PO4_in*0.1

def CSTR_investment_cost (F_total, total_time, mixing_operation):
    from global_parameters_module import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref, density, latent_heat_evap, nat_gas_heat_value
    from feedstock_input_module import elements_wet, elements_dry, nutrients, feedstock_parameters, elements_dry_comp
    from equipment_costs.vessel_design_cost import vessel_design_cost
    from equipment_costs.agitator_design_cost import agitator_design_cost
    
    #Struvite formaiton
    #K_ps            = 7.08E-14 # solubility product doi:10.1016/S0960-8524(03)00076-2
    #k               = 12.3/3600 #s-1 reaction kinetic constant 1st order. Struvite precipitation in anaerobic swine lagoon liquid: effect of pH and Mg:P ratio and determination of rate constant . Nelson et al, 2003
    #G               = 1E-2*1E-6 # m/s 10.1007/s11696-018-0613-5 Induction time is negigible (10.1016/j.watres.2013.03.007)
    #L_crystal       = 40E-6 # m 10.1007/s11696-018-0613-5    10.1016/j.cej.2012.10.038
    
    #-------------------------Residence time----------------------------------
    #NH4_molar               = ((fc_N_NH3_in)/MW["N"])/((F_total/feedstock_parameters['digestate_density'])*UnitConv['L_to_m3'])
    #Mg_molar                = ((fc_MgCl2_in)/MW["MgCl2"])/((F_total/feedstock_parameters['digestate_density'])*UnitConv['L_to_m3'])
    #PO4_molar               = ((fc_P_PO4_in)/MW["P"])/((F_total/feedstock_parameters['digestate_density'])*UnitConv['L_to_m3'])
    #PO4_molar_equilibrium   = K_ps/(NH4_molar*Mg_molar)
    
    #reaction_time           = (np.log((PO4_molar*(1-(fc_P_PO4_out/fc_P_PO4_in)))-PO4_molar_equilibrium)-np.log(PO4_molar-PO4_molar_equilibrium))/(-k) #(s)
    #growth_time             = L_crystal/G
    #total_time              = reaction_time+growth_time#(s)
    
    #-------------------------Reactor vessel----------------------------------
    vessel_results = vessel_design_cost(F_total, total_time)
    vessel_V_total = vessel_results['Volume']
    #Results
    vessel_V = vessel_results['V_design']
    vessel_D = vessel_results['D_design']
    vessel_L = vessel_results['L_design']
    n_vessels = vessel_results['n_vessels']
    vessels_cost_2016 =  vessel_results['vessels_cost_2016']
    
    #-------------------------Agitator design----------------------------------
    #mixing_operation='Slurries' #Operation types: 'Blending','Homogeneous reaction','Reaction with heat transfer','Liquid-liquid mixtures','Liquid-gas mixtures','Slurries'
    agitator_results = agitator_design_cost (mixing_operation, vessel_results['V_design'], vessel_results['n_vessels'])
    #Results
    agitator_power = agitator_results['agitator_power']
    n_agitators = agitator_results['n_agitators']
    cost_agitator_2016 = agitator_results['cost_agitator_2016']
    operation_cost_agitator_2016 = agitator_results['operation_cost_agitator_2016']
    
    #-------------------------CSTR cost----------------------------------
    CSTR_cost_2016 = vessel_results['vessels_cost_2016'] + agitator_results['cost_agitator_2016']
    CSTR_operation_cost_2016 = operation_cost_agitator_2016
    
    
    return {'reactor_V':vessel_results['V_design'], 'reactor_D':vessel_results['D_design'], 'reactor_L':vessel_results['L_design'], 'agitator_power':agitator_results['agitator_power'], 'n_reactors':vessel_results['n_vessels'], 'CSTR_cost_2016':CSTR_cost_2016, 'CSTR_operation_cost_2016':CSTR_operation_cost_2016}   
    
        

#pressure_filter_flow = [i for i in flow_vector if i<=19]
#gravity_filter_flow = [i for i in flow_vector if i>19]

#plt.figure()
#plt.plot(pressure_filter_flow, filter_package_investment_cost_1979_USD_store[:len(pressure_filter_flow)])
#plt.plot(gravity_filter_flow,filter_package_investment_cost_1979_USD_store[len(pressure_filter_flow):])
##plt.legend(loc='upper left')
#plt.title('Filter (package, gravity) investment cost (SI) \n (all costs included except filtration media)')
#plt.xlabel("Filter flow $ (m^{3}/h) $")
#plt.ylabel('Cost (1979 USD)')
#plt.savefig("filter_package_investment_cost_m.pdf", bbox_inches='tight')
