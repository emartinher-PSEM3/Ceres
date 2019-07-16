# ===============================================================================================================================================================================================================================
# ###############################################################################################################################################################################################################################
# ===============================================================================================================================================================================================================================
# IMPORT LIBRARIES MODULE
import numpy as np
import pandas as pd
import scipy.optimize as opt
from scipy.integrate import odeint, solve_bvp
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

#F_tot = 30
def screw_press_cost_module(F_tot): #F_tot is measured in m3/day

    from global_parameters_module import UnitConv, MW, c_p_liq_sol, dH_vap_0, Tc, Tb, dH_f, dH_c, c_p_v_1, c_p_v_2, c_p_v_3, c_p_v_4, coef_vapor_pressure_1, coef_vapor_pressure_2, coef_vapor_pressure_3, CEI, price, nu_p, k_p, n_watson, epsilon, T_amb, P_ref, density, latent_heat_evap, nat_gas_heat_value
    from feedstock_input_module import elements_wet, elements_dry, nutrients, feedstock_parameters, elements_dry_comp
    from economic_parameters_module import ec_param
    
    
    #SIZES FOR SCREW PRESS FOR SLUDGE DEWATERING (PWTech)
    
    #PWTech http://pwtech.us/HTML/addResources.html
    diameter_inch = np.array([9.1, 13.8, 16.5, 16.5, 16.5, 22.25, 22.25, 22.25])
    diameter_m = diameter_inch*UnitConv['inch_to_m']
    
    n_units = np.array([1, 1, 1, 2, 3, 2, 3, 4])
    
    flow_GPM = np.array([8, 15, 35, 70, 105, 130, 200, 265])
    flow_cuft_hr = flow_GPM*UnitConv['GPM_to_cuft_hr']
    flow_m3_day = flow_cuft_hr*UnitConv['cuft_to_m3']*24
    
    power_HP = np.array([0.4, 0.6, 1.2, 1.7, 2.7, 5.2, 8.5, 10.5])
    power_kW = power_HP*UnitConv['HP_to_kW']
    
    ScrewPress_diameter = []
    n_ScrewPress = []
    power_kW_ScrewPress = []
    
    if F_tot <= flow_m3_day[0]:
        ScrewPress_diameter = diameter_m[0]
        n_ScrewPress = n_units[0]
        power_kW_ScrewPress = power_kW[0]
    
    elif flow_m3_day[0] < F_tot <= flow_m3_day[-1]:
        for i in flow_m3_day[:-1]:
            index = np.int(np.where(flow_m3_day == i)[0])
            if flow_m3_day[index] < F_tot <= flow_m3_day[index+1]:
                ScrewPress_diameter = diameter_m[index+1]
                n_ScrewPress = n_units[index+1]
                power_kW_ScrewPress = power_kW[index+1]
                break
                
    elif F_tot > flow_m3_day[-1]:
        ScrewPress_diameter = diameter_m[-1]
        n_ScrewPress = np.ceil(F_tot/(flow_m3_day[5]/2))
        power_kW_ScrewPress = power_kW[-1]
        
        
    # =============================================================================
    # Cost
    # =============================================================================
    screwpress_cost_2014_USD = n_ScrewPress*(23221.804*ScrewPress_diameter**2+24708.740*ScrewPress_diameter - 2547.881)
    screwpress_cost_2016_USD = screwpress_cost_2014_USD*(CEI[2016]/CEI[2014])
    
    screwpress_PPC_2016_USD = 3.15*screwpress_cost_2016_USD
    investment_cost = 1.4*screwpress_PPC_2016_USD
    
    if F_tot <= flow_m3_day[-1]:
        operation_cost_2016_non_amortized = power_kW_ScrewPress*3600*price['electricity'] #USD/year
        operation_cost_2016_amortized = power_kW_ScrewPress*3600*price['electricity']+investment_cost/ec_param['plant_lifetime'] #USD/year
    elif F_tot > flow_m3_day[-1]:
        operation_cost_2016_non_amortized = power_kW_ScrewPress*3600*price['electricity']*(n_ScrewPress/4) #USD/year
        operation_cost_2016_amortized = power_kW_ScrewPress*3600*price['electricity']*(n_ScrewPress/4)+investment_cost/ec_param['plant_lifetime'] #USD/year
    
    return {'ScrewPress_diameter':ScrewPress_diameter, 'n_ScrewPress':n_ScrewPress, 'power_kW_ScrewPress':power_kW_ScrewPress, 
            'equipment_cost':screwpress_cost_2016_USD,
            'screwpress_PPC':screwpress_PPC_2016_USD,
            'investment_cost':investment_cost,
            'operation_cost_2016_non_amortized':operation_cost_2016_non_amortized,
            'operation_cost_2016_amortized':operation_cost_2016_amortized,
            }
    
    
#plot_unitcost_store =[]
#plot_operational_cost_store =[]
#for i in np.linspace(1, 1600, 100):
    #F_tot = i
    #ScrewPress_result = screw_press_cost_module(F_tot)
    #plot_unitcost_store.append(ScrewPress_result['screwpress_cost'])
    #plot_operational_cost_store.append(ScrewPress_result['screwpress_operational_cost'])

#plt.figure(0)
#plt.plot(np.linspace(1, 1600, 100), plot_unitcost_store)
#plt.legend(loc='upper left')
#plt.title('Screw press fixed cost (SI)')
#plt.xlabel("Flow $ (m^3 / day) $")
#plt.ylabel('Fixed cost 2016 USD')
#plt.savefig("screwpress_unit_cost_m.pdf")

#plt.figure(1)
#plt.plot(np.linspace(1, 1600, 100), plot_operational_cost_store)
#plt.legend(loc='upper left')
#plt.title('Screw press fixed cost (SI)')
#plt.xlabel("Flow $ (m^3 / day) $")
#plt.ylabel('Operational cost 2016 USD/year')
#plt.savefig("screwpress_op_cost_m.pdf")
##        
##elif flow_m3_day[0] < F_tot <= flow_m3_day[1]:
##    ScrewPress_diameter = diameter_m[1]
##    
##elif flow_m3_day[1] < F_tot <= flow_m3_day[2]:
##    ScrewPress_diameter = diameter_m[2]
##    
##elif flow_m3_day[2] < F_tot <= flow_m3_day [3]:
##    ScrewPress_diameter = diameter_m[3]
#    
#    
#    
#    
#    
#    
#elif F_tot > flow_m3_day[2]:
#    ScrewPress_diameter = FBR_size_array[2]
#
#
#
##Fit
##def screwpress_size(xdata, a):
##    return (a**xdata) #Negative exp function
#
#def screwpress_size(xdata, a, b, c, d):
#    return a*xdata*xdata*xdata+b*xdata*xdata+c*xdata+d #Third order poly 
#
##def screwpress_size(xdata, a, b, c):
##    return a*xdata*xdata+b*xdata+c #Second order poly
#    
##def screwpress_size(xdata, a, b):
##    return a*xdata+b #Fist order poly
#
##def screwpress_size(xdata, a, b, c, d, e):
##    return a*xdata*xdata*xdata*xdata+b*xdata*xdata*xdata+c*xdata*xdata+d*xdata+e #Fourth order poly
#
##def screwpress_size(xdata, a, b, c):
##    return a/(1+((xdata)*b)**(c)) #Sigmoidal function
#
##def screwpress_cost(xdata, a, b):
##    return a*(np.tanh(xdata))+b #-tanh function (hyperbolic)
#
## Meters
#plt.figure()
#parameters_screwpress_size_m, cov_screwpress_size_m = curve_fit(screwpress_size, flow_m3_day, diameter_m)
##
##with sns.plotting_context("paper") and sns.axes_style("darkgrid"):
##    sns.relplot(x="Ca", y="StrYield", kind="line", ci=90, color="red", data=bigdata, label='Average results and 90% confidence interval')
#plt.scatter(flow_m3_day, diameter_m)
#plt.plot(flow_m3_day, screwpress_size(flow_m3_day, *parameters_screwpress_size_m), 'k--', label='Fit: a=%5.3e, b=%5.3e, \n      c=%5.3e,  d=%5.3e' % tuple(parameters_screwpress_size_m)) #label='Fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(parameters_StrYield)
#plt.legend(loc='upper left')
#plt.title('Screw press size (SI)')
#plt.xlabel("Flow $ (m^{3} / day) $")
#plt.ylabel("Screw press diameter $ (m) $")
#plt.savefig("screwpress_size_m.pdf")
#
#
##Inches
#plt.figure()
#parameters_screwpress_size_inch, cov_screwpress_size_inch = curve_fit(screwpress_size, flow_m3_day, diameter_inch)
##
##with sns.plotting_context("paper") and sns.axes_style("darkgrid"):
##    sns.relplot(x="Ca", y="StrYield", kind="line", ci=90, color="red", data=bigdata, label='Average results and 90% confidence interval')
#plt.plot(flow_m3_day, diameter_inch)
#plt.plot(flow_m3_day, screwpress_size(flow_m3_day, *parameters_screwpress_size_inch), 'k--', label='Fit: a=%5.3e, b=%5.3e, \n      c=%5.3e,  d=%5.3e' % tuple(parameters_screwpress_size_inch)) #label='Fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(parameters_StrYield)
#plt.legend(loc='upper left')
#plt.title('Screw press size (British Empire)')
#plt.xlabel("Flow $ (m^{3} / day) $")
#plt.ylabel("Screw press diameter $ (inch) $")
#plt.savefig("screwpress_size_inch.pdf")
#
#
##Power
#
##Fit
##def screwpress_power(xdata, a):
##    return (a**xdata) #Negative exp function
#
##def screwpress_power(xdata, a, b, c, d):
##    return a*xdata*xdata*xdata+b*xdata*xdata+c*xdata+d #Third order poly
#
#def screwpress_power(xdata, a, b, c):
#    return a*xdata*xdata+b*xdata+c #Second order poly
#    
##def screwpress_power(xdata, a, b):
##    return a*xdata+b #Fist order poly
#
##def screwpress_power(xdata, a, b, c, d, e):
##    return a*xdata*xdata*xdata*xdata+b*xdata*xdata*xdata+c*xdata*xdata+d*xdata+e #Fourth order poly
#
##def screwpress_power(xdata, a, b, c):
##    return a/(1+((xdata)*b)**(c)) #Sigmoidal function
#
##def screwpress_power(xdata, a, b):
##    return a*(np.tanh(xdata))+b #-tanh function (hyperbolic)
#    
#plt.figure()
#parameters_screwpress_power, cov_screwpress_power = curve_fit(screwpress_power, flow_m3_day, power_kW)
##
##with sns.plotting_context("paper") and sns.axes_style("darkgrid"):
##    sns.relplot(x="Ca", y="StrYield", kind="line", ci=90, color="red", data=bigdata, label='Average results and 90% confidence interval')
#plt.plot(flow_m3_day, power_kW)
#plt.plot(flow_m3_day, screwpress_power(flow_m3_day, *parameters_screwpress_power), 'k--', label='Fit: a=%5.3e, b=%5.3e, c=%5.3e' % tuple(parameters_screwpress_power)) #label='Fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(parameters_StrYield)
#plt.legend(loc='upper left')
#plt.title('Screw press power (SI)')
#plt.xlabel("Flow $ (m^{3} / day) $")
#plt.ylabel("Screw press power $ (kW) $")
#plt.savefig("screwpress_power_kW.pdf")
