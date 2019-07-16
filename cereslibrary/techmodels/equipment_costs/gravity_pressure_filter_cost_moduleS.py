import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#from global_parameters_module import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref

def filter_package_investment_cost (flow):
    from global_parameters_moduleS import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref, density, latent_heat_evap, nat_gas_heat_value

    #EPA Estimating Water Treatment Costs 1979 Package Gravity and Pressure Filter Plants
    filter_package_intervalsflow_gpm = np.array([0.7, 1.7, 7, 17, 28, 80, 170, 287.5, 420, 630, 1400])
    filter_package_flow_m3_hr = filter_package_intervalsflow_gpm*UnitConv['GPM_to_cuft_hr']*UnitConv['cuft_to_m3']

    filter_type_store = ['Pressure', 'Gravity']

    filter_package_investment_cost_1979_USD = np.array([19020, 30250, 41480, 52610, 63740, 151320, 189850, 214280, 254750, 463450])

    filter_package_investment_cost_1979_USD_store=0
    filter_type = []
    n_filters = []
    status = 'OK'
    #flow_vector = np.arange(0.16, 318, 0.1)
    #for flow in flow_vector:
    if filter_package_flow_m3_hr[0] <= flow < filter_package_flow_m3_hr[1]:
        filter_type = filter_type_store[0]
        n_filters = 1
        filter_package_investment_cost_1979_USD_store=(filter_package_investment_cost_1979_USD[0])
        
    elif filter_package_flow_m3_hr[1] <= flow < filter_package_flow_m3_hr[2]:
        filter_type = filter_type_store[0]
        n_filters = 1
        filter_package_investment_cost_1979_USD_store=(filter_package_investment_cost_1979_USD[1])
        
    elif filter_package_flow_m3_hr[2] <= flow < filter_package_flow_m3_hr[3]:
        filter_type = filter_type_store[0]
        n_filters = 1
        filter_package_investment_cost_1979_USD_store=(filter_package_investment_cost_1979_USD[2])
        
    elif filter_package_flow_m3_hr[3] <= flow < filter_package_flow_m3_hr[4]:
        filter_type = filter_type_store[0]
        n_filters = 1
        filter_package_investment_cost_1979_USD_store=(filter_package_investment_cost_1979_USD[3])
        
    elif filter_package_flow_m3_hr[4] <= flow < filter_package_flow_m3_hr[5]:
        filter_type = filter_type_store[0]
        n_filters = 1
        filter_package_investment_cost_1979_USD_store=(filter_package_investment_cost_1979_USD[4])
        
    elif filter_package_flow_m3_hr[5] <= flow < filter_package_flow_m3_hr[6]:
        filter_type = filter_type_store[1]
        n_filters = 2
        filter_package_investment_cost_1979_USD_store=(filter_package_investment_cost_1979_USD[5])
        
    elif filter_package_flow_m3_hr[6] <= flow < filter_package_flow_m3_hr[7]:
        filter_type = filter_type_store[1]
        n_filters = 2
        filter_package_investment_cost_1979_USD_store=(filter_package_investment_cost_1979_USD[6])
        
    elif filter_package_flow_m3_hr[7] <= flow < filter_package_flow_m3_hr[8]:
        filter_type = filter_type_store[1]
        n_filters = 2
        filter_package_investment_cost_1979_USD_store=(filter_package_investment_cost_1979_USD[7])
        
    elif filter_package_flow_m3_hr[8] <= flow < filter_package_flow_m3_hr[9]:
        filter_type = filter_type_store[1]
        n_filters = 2
        filter_package_investment_cost_1979_USD_store=(filter_package_investment_cost_1979_USD[8])
        
    elif filter_package_flow_m3_hr[9] <= flow <= filter_package_flow_m3_hr[10]:
        filter_type = filter_type_store[1]
        n_filters = 2
        filter_package_investment_cost_1979_USD_store=(filter_package_investment_cost_1979_USD[9])
        
    else:
        status = 'FLOW OUT OF BOUNDS (min 0.17, max 317 m3/h)'
    
    filter_package_investment_cost_2016_USD = filter_package_investment_cost_1979_USD_store*(CEI[2016]/CEI[1979])
    
    return {'filter_type':filter_type, 'n_filters':n_filters, 'filter_package_investment_cost_2016_USD':filter_package_investment_cost_2016_USD, 'status':status}
        

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


def filter_package_operation_cost (flow):
    from global_parameters_moduleS import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref

    #EPA Estimating Water Treatment Costs 1979 Package Gravity and Pressure Filter Plants
    filter_package_intervalsflow_gpm = np.array([0.7, 1.7, 7, 17, 28, 80, 170, 287.5, 420, 630, 1400])
    filter_package_flow_m3_hr = filter_package_intervalsflow_gpm*UnitConv['GPM_to_cuft_hr']*UnitConv['cuft_to_m3']

    filter_package_operation_cost_1979_USD = np.array([4440, 4600, 4760, 5400, 6040, 35090, 36375, 43990, 44345, 58680])

    filter_package_operation_cost_1979_USD_store=0
    status = 'OK'
    #flow_vector = np.arange(0.16, 318, 0.1)
    #for flow in flow_vector:
    if filter_package_flow_m3_hr[0] <= flow < filter_package_flow_m3_hr[1]:
        filter_package_operation_cost_1979_USD_store=(filter_package_operation_cost_1979_USD[0])
        
    elif filter_package_flow_m3_hr[1] <= flow < filter_package_flow_m3_hr[2]:
        filter_package_operation_cost_1979_USD_store=(filter_package_operation_cost_1979_USD[1])
        
    elif filter_package_flow_m3_hr[2] <= flow < filter_package_flow_m3_hr[3]:
        filter_package_operation_cost_1979_USD_store=(filter_package_operation_cost_1979_USD[2])
        
    elif filter_package_flow_m3_hr[3] <= flow < filter_package_flow_m3_hr[4]:
        filter_package_operation_cost_1979_USD_store=(filter_package_operation_cost_1979_USD[3])
        
    elif filter_package_flow_m3_hr[4] <= flow < filter_package_flow_m3_hr[5]:
        filter_package_operation_cost_1979_USD_store=(filter_package_operation_cost_1979_USD[4])
        
    elif filter_package_flow_m3_hr[5] <= flow < filter_package_flow_m3_hr[6]:
        filter_package_operation_cost_1979_USD_store=(filter_package_operation_cost_1979_USD[5])
        
    elif filter_package_flow_m3_hr[6] <= flow < filter_package_flow_m3_hr[7]:
        filter_package_operation_cost_1979_USD_store=(filter_package_operation_cost_1979_USD[6])
        
    elif filter_package_flow_m3_hr[7] <= flow < filter_package_flow_m3_hr[8]:
        filter_package_operation_cost_1979_USD_store=(filter_package_operation_cost_1979_USD[7])
        
    elif filter_package_flow_m3_hr[8] <= flow < filter_package_flow_m3_hr[9]:
        filter_package_operation_cost_1979_USD_store=(filter_package_operation_cost_1979_USD[8])
        
    elif filter_package_flow_m3_hr[9] <= flow <= filter_package_flow_m3_hr[10]:
        filter_package_operation_cost_1979_USD_store=(filter_package_operation_cost_1979_USD[9])
    else:
        status = 'FLOW OUT OF BOUNDS (min 0.17, max 317 m3/h)'
    
    filter_package_operation_cost_2016_USD = filter_package_operation_cost_1979_USD_store*(CEI[2016]/CEI[1979])
    
    return {'filter_package_operation_cost_2016_USD':filter_package_operation_cost_2016_USD, 'status':status}
    
#pressure_filter_flow = [i for i in flow_vector if i<=19]
#gravity_filter_flow = [i for i in flow_vector if i>19]

#plt.figure()
#plt.plot(pressure_filter_flow, filter_package_operation_cost_1979_USD_store[:len(pressure_filter_flow)])
#plt.plot(gravity_filter_flow,filter_package_operation_cost_1979_USD_store[len(pressure_filter_flow):])
##plt.legend(loc='upper left')
#plt.title('Filter (package, gravity) operation cost (SI) \n (all costs included except filtration media)')
#plt.xlabel("Filter flow $ (m^{3}/h) $")
#plt.ylabel('Cost (1979 USD)')
#plt.savefig("filter_package_operation_cost_m.pdf", bbox_inches='tight')


