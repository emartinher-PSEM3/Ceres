#N_animals = 3000
def main_function(N_animals, AD_eval): 
    import numpy as np
    import pandas as pd
    
    
    from feedstock_input_module import elements_wet, elements_dry, nutrients, feedstock_parameters, elements_dry_comp
    
    from AD_module import AD_module
    from screw_press_module import screw_press_module
    from filtration_modulev3 import filtration_module
    from FBR_v2 import FBR_module
    from CSTR_v4 import CSTR_module
    
    # =====================================================================================
    # #####################################################################################
    # =====================================================================================
    # SETS, PARAMETERS AND NODES DATA ACQUISITION
#    nodes_matrix            = pd.read_csv('nodes/nodes_main.csv', sep=",", header=None)
#    nodes                   = np.array(nodes_matrix[0].dropna())   
#    process_elements_digestor_matrix = pd.read_csv('process_elements/process_elements_digestor.csv', sep=",", header=0)
#    process_elements_FBR_matrix = pd.read_csv('process_elements/process_elements_FBR.csv', sep=",", header=0)
#    process_elements_CSTR_matrix = pd.read_csv('process_elements/process_elements_CSTR.csv', sep=",", header=0)
    
    nodes_matrix            = pd.read_csv('cereslibrary/techmodels/nodes/nodes_main.csv', sep=",", header=None)
    nodes                   = np.array(nodes_matrix[0].dropna())       
    process_elements_digestor_matrix = pd.read_csv('cereslibrary/techmodels/process_elements/process_elements_digestor.csv', sep=",", header=0)
    process_elements_FBR_matrix = pd.read_csv('cereslibrary/techmodels/process_elements/process_elements_FBR.csv', sep=",", header=0)
    process_elements_CSTR_matrix = pd.read_csv('cereslibrary/techmodels/process_elements/process_elements_CSTR.csv', sep=",", header=0)
    
    # =====================================================================================
    # #####################################################################################
    # =====================================================================================
    # MANURE DATA ACQUISITION AND COMPOSITION SETTLEMENT   
    #chemicals_comp   = np.array(process_elements_matrix["Component"][3:7].dropna())
    #chemicals_conc   = np.full((len(chemicals_comp)), 0)
    #chemicals        = dict(zip(chemicals_comp, chemicals_conc))
    #
    #products_comp    = np.array(process_elements_matrix["Component"][0:3].dropna())
    #product_conc     = np.full((len(products_comp)), 0)
    #product          = dict(zip(products_comp, product_conc))
    
    # =====================================================================================
    # #####################################################################################
    # =====================================================================================
    #FLOW TO BE TREATED
    F_ini = N_animals*feedstock_parameters['cattle_manure_ratio']/24/3600 #kg/s
    
    # =====================================================================================
    # #####################################################################################
    # =====================================================================================
    # TOTAL ELEMENTS
    gases_comp   = np.array(process_elements_digestor_matrix["Component"].dropna())
    gases_conc   = np.full((len(gases_comp)), 0)
    gases        = dict(zip(gases_comp, gases_conc))
    
    chemicalsFBR_comp   = np.array(process_elements_FBR_matrix["Component"][3:8].dropna())
    chemicalsFBR_conc   = np.full((len(chemicalsFBR_comp)), 0)
    chemicalsFBR        = dict(zip(chemicalsFBR_comp, chemicalsFBR_conc))
    
    productsFBR_comp       = np.array(process_elements_FBR_matrix["Component"][0:3].dropna())
    productFBR_conc      = np.full((len(productsFBR_comp)), 0)
    productFBR            = dict(zip(productsFBR_comp, productFBR_conc))
    
    chemicalsCSTR_comp   = np.array(process_elements_CSTR_matrix["Component"][3:7].dropna())
    chemicalsCSTR_conc   = np.full((len(chemicalsCSTR_comp)), 0)
    chemicalsCSTR        = dict(zip(chemicalsCSTR_comp, chemicalsCSTR_conc))
    
    productsCSTR_comp    = np.array(process_elements_CSTR_matrix["Component"][0:3].dropna())
    productCSTR_conc     = np.full((len(productsCSTR_comp)), 0)
    productCSTR          = dict(zip(productsCSTR_comp, productCSTR_conc))
        
    #total_elements = {**elements_wet,**chemicals,**product} # Merge the two dictionaries
    total_elements = {**elements_wet,**gases,**chemicalsFBR,**productFBR,**chemicalsCSTR,**productCSTR}
    
    # =====================================================================================
    # #####################################################################################
    # =====================================================================================
    ## VARIABLES DEFINITION (IN NESTED DICTIONARIES) (INITIALIZATION)
    nodes_list              = nodes.tolist()
    initialization_comp     = total_elements
    initialization_nan      = np.full((len(initialization_comp)), 0)
    
    fc = {key: dict(zip(initialization_comp,initialization_nan)) for key in nodes_list}
    
    x = {key: dict(zip(initialization_comp,initialization_nan)) for key in nodes_list}
    
    F = {key: np.nan for key in nodes_list}
    
    # =====================================================================================
    # #####################################################################################
    # =====================================================================================
    # INITIAL FLOWS
    for i in elements_wet.keys():
        x["Src1ConsistencyEval"][i]  = total_elements[i]/100
        fc["Src1ConsistencyEval"][i] = x["Src1ConsistencyEval"][i]*F_ini
    F["Src1ConsistencyEval"] = F_ini
    
    # =============================================================================
    # TS evaluation
    # =============================================================================
    
    # Manure as transferred for utilization consitency evalutaiton
    TS_max = 0.3 #https://doi.org/10.1016/j.biortech.2012.01.174
    
    if feedstock_parameters['TS'] <= TS_max:
        for i in elements_wet.keys():
            fc["ConsistencyEvalADEval"][i] = fc["Src1ConsistencyEval"][i]
            x["ConsistencyEvalADEval"][i] = x["Src1ConsistencyEval"][i]
            F["ConsistencyEvalADEval"] = F["Src1ConsistencyEval"]
    else:
        current_flow = F_ini
        additional_Wa = (feedstock_parameters['TS']*F_ini)/TS_max-F_ini
        F["ConsistencyEvalADEval"] = F["Src1ConsistencyEval"]+additional_Wa
        fc["ConsistencyEvalADEval"]['Wa'] = fc["Src1ConsistencyEval"]['Wa'] + additional_Wa
        for i in (i for i in elements_wet.keys() if i!="Wa"):
            fc["ConsistencyEvalADEval"][i] = fc["Src1ConsistencyEval"][i]
        for ii in elements_wet.keys():
            x['ConsistencyEvalADEval'][ii] = fc['ConsistencyEvalADEval'][ii]/(F["ConsistencyEvalADEval"])
     
        
    # =============================================================================
    # AD evaluation
    # =============================================================================
    AD_results = AD_module(F["ConsistencyEvalADEval"],fc["ConsistencyEvalADEval"], x["ConsistencyEvalADEval"], N_animals)
    #AD evaluaiton here
    #AD_eval = []
    #AD_eval = 'Accepted'
    #AD_eval = None
    if AD_eval:
        for i in {**elements_wet,**gases}.keys():
            fc["ADEvalSLSep"][i] = AD_results['fc']['BioreactorSink2'][i]
            x["ADEvalSLSep"][i] = AD_results['x']['BioreactorSink2'][i]
            
            fc["ADEvalBiogas"][i] = AD_results['fc']['BioreactorSink1'][i]
            x["ADEvalBiogas"][i] = AD_results['x']['BioreactorSink1'][i]
            
        F["ADEvalSLSep"] = AD_results['F']['BioreactorSink2']
        F["ADEvalBiogas"] = AD_results['F']['BioreactorSink1']
            
    if not AD_eval:
        for i in elements_wet.keys():
            fc["ADEvalSLSep"][i] = fc["Src1ConsistencyEval"][i]
            x["ADEvalSLSep"][i] = x["Src1ConsistencyEval"][i]
        F["ADEvalSLSep"] = F["Src1ConsistencyEval"]
            
   # =============================================================================
   # SL separation
   # =============================================================================
    ScrewPress_results = screw_press_module(F["ADEvalSLSep"],fc["ADEvalSLSep"],x["ADEvalSLSep"])
    
    for i in elements_wet.keys():
        fc["SLSepLiqTreatment"][i] = ScrewPress_results['fc']['ScrewPressSink2'][i]
        x["SLSepLiqTreatment"][i]  = ScrewPress_results['x']['ScrewPressSink2'][i]
       
        fc["SLSepLiqSolidTreatment"][i] = ScrewPress_results['fc']['ScrewPressSink1'][i]
        x["SLSepLiqSolidTreatment"][i]  = ScrewPress_results['x']['ScrewPressSink1'][i]
       
    F["SLSepLiqTreatment"] = ScrewPress_results['F']['ScrewPressSink2']
    F["SLSepLiqSolidTreatment"] = ScrewPress_results['F']['ScrewPressSink1']
   
#    # =============================================================================
#    # L treatments
#    # =============================================================================
#    #FILTRATION
    filtration_module_results = filtration_module(F["SLSepLiqTreatment"],fc["SLSepLiqTreatment"],x["SLSepLiqTreatment"])
    for i in elements_wet.keys():
        fc["LiqTreatmentFilterSnk1"][i] = filtration_module_results['fc']['FilterSink1'][i]
        x["LiqTreatmentFilterSnk1"][i]  = filtration_module_results['x']['FilterSink1'][i]
        
        fc["LiqTreatmentFilterSnk2"][i] = filtration_module_results['fc']['FilterSink2'][i]
        x["LiqTreatmentFilterSnk2"][i]  = filtration_module_results['x']['FilterSink2'][i]
        
    F["LiqTreatmentFilterSnk1"] = filtration_module_results['F']['FilterSink1']
    F["LiqTreatmentFilterSnk2"] = filtration_module_results['F']['FilterSink2']
    #    
#    
#    #FBR Struvite
    FBR_module_results = FBR_module(F["SLSepLiqTreatment"],fc["SLSepLiqTreatment"],x["SLSepLiqTreatment"])
    for i in {**elements_wet,**chemicalsFBR,**productFBR}.keys():
        fc["LiqTreatmentFBRSnk4"][i] = FBR_module_results['fc']['DryerSink4'][i]
        x["LiqTreatmentFBRSnk4"][i]  = FBR_module_results['x']['DryerSink4'][i]
        
        fc["LiqTreatmentFBRSnk3"][i] = FBR_module_results['fc']['DryerSink3'][i]
        x["LiqTreatmentFBRSnk3"][i]  = FBR_module_results['x']['DryerSink3'][i]
        
        fc["LiqTreatmentFBRSnk2"][i] = FBR_module_results['fc']['HydrocycloneSink2'][i]
        x["LiqTreatmentFBRSnk2"][i]  = FBR_module_results['x']['HydrocycloneSink2'][i]
        
    #    fc["LiqTreatmentFBRSnk1"][i] = FBR_module_results['fc']['HydrocycloneSink1'][i]
    #    x["LiqTreatmentFBRSnk1"][i]  = FBR_module_results['x']['HydrocycloneSink1'][i]
        
    F["LiqTreatmentFBRSnk4"] = FBR_module_results['F']['DryerSink4']
    F["LiqTreatmentFBRSnk3"] = FBR_module_results['F']['DryerSink3']
    F["LiqTreatmentFBRSnk2"] = FBR_module_results['F']['HydrocycloneSink2']
    #F["LiqTreatmentFBRSnk1"] = FBR_module_results['F']['HydrocycloneSink1']
#    
#    
#    #CSTR Struvite
    CSTR_module_results = CSTR_module(F["SLSepLiqTreatment"],fc["SLSepLiqTreatment"],x["SLSepLiqTreatment"])
    
    for i in {**elements_wet,**chemicalsCSTR,**productCSTR}.keys():
        fc["LiqTreatmentCSTRSnk3"][i] = CSTR_module_results['fc']['DryerSink3'][i]
        x["LiqTreatmentCSTRSnk3"][i]  = CSTR_module_results['x']['DryerSink3'][i]
        
        fc["LiqTreatmentCSTRSnk2"][i] = CSTR_module_results['fc']['DryerSink2'][i]
        x["LiqTreatmentCSTRSnk2"][i]  = CSTR_module_results['x']['DryerSink2'][i]
        
        fc["LiqTreatmentCSTRSnk4"][i] = CSTR_module_results['fc']['ClarifSink4'][i]
        x["LiqTreatmentCSTRSnk4"][i]  = CSTR_module_results['x']['ClarifSink4'][i]
        
        fc["LiqTreatmentCSTRSnk1"][i] = CSTR_module_results['fc']['BeltFiltSink1'][i]
        x["LiqTreatmentCSTRSnk1"][i]  = CSTR_module_results['x']['BeltFiltSink1'][i]
        
    F["LiqTreatmentCSTRSnk3"] = CSTR_module_results['F']['DryerSink3']
    F["LiqTreatmentCSTRSnk2"] = CSTR_module_results['F']['DryerSink2']
    F["LiqTreatmentCSTRSnk4"] = CSTR_module_results['F']['ClarifSink4']
    F["LiqTreatmentCSTRSnk1"] = CSTR_module_results['F']['BeltFiltSink1']
    
    
    #Summary of results P
    results_summary_data = {'Fraction TP recovered':[filtration_module_results['fraction_recoved_TP'],FBR_module_results['fraction_recoved_TP'],CSTR_module_results['fraction_recoved_TP'], 0],
                            'Fraction TP released':[filtration_module_results['fraction_released_TP'],FBR_module_results['fraction_released_TP'],CSTR_module_results['fraction_released_TP'], 0],
                            'Fraction PO4 recovered':[filtration_module_results['fraction_recoved_PO4'],FBR_module_results['fraction_recoved_PO4'],CSTR_module_results['fraction_recoved_PO4'], 0],
                            'Fraction PO4 released':[filtration_module_results['fraction_released_PO4'],FBR_module_results['fraction_released_PO4'],CSTR_module_results['fraction_released_PO4'], 0],
                            'PO4 emissions (mg/L)':[filtration_module_results['PO4_conc_released'],FBR_module_results['PO4_conc_released'],CSTR_module_results['PO4_conc_released'], 0],
                            'Carbon efficiency': [0, 0, 0, AD_results['carbon_efficiency']]
                                } 
    results_summary = pd.DataFrame(results_summary_data, index=['Filtration','FBR struvite','CSTR struvite','Anaerobic digestion'])
    results_summary = results_summary.applymap('{0:.2f}'.format)
    #.map('${:,.2f}'.format)

    #Economic summary of results
    investment_cost                 = {'Investment cost':[AD_results['investment_cost'], ScrewPress_results['investment_cost'], filtration_module_results['investment_cost'],FBR_module_results['investment_cost'], CSTR_module_results['investment_cost']],
                                }
    operation_cost_non_amortized    = {'Operation cost non amortized':[AD_results['operation_cost_2016_non_amortized'], ScrewPress_results['operation_cost_2016_non_amortized'], filtration_module_results['operation_cost_2016_non_amortized'],FBR_module_results['operation_cost_2016_non_amortized'], CSTR_module_results['operation_cost_2016_non_amortized']],
                                }
    operation_cost_amortized        = {'Operation cost amortized':[AD_results['operation_cost_2016_amortized'], ScrewPress_results['operation_cost_2016_amortized'], filtration_module_results['operation_cost_2016_amortized'],FBR_module_results['operation_cost_2016_amortized'], CSTR_module_results['operation_cost_2016_amortized']],
                                }
    input_cash        = {'Input cash':[0, 0, 0,FBR_module_results['Struvite_benefits'], CSTR_module_results['Struvite_benefits']],
                                }
    
    equipment_cost = {'Equipment_cost':[AD_results['investment_cost'], ScrewPress_results['equipment_cost'],  filtration_module_results['investment_cost'],FBR_module_results['equipment_cost'],CSTR_module_results['equipment_cost']],
                                }
    economic_results_summary = pd.DataFrame({**equipment_cost, **investment_cost, **operation_cost_non_amortized, **operation_cost_amortized, **input_cash}, index=['Anaerobic digestion', 'Screw Press', 'Filtration','FBR struvite','CSTR struvite'])
    economic_results_summary = economic_results_summary.applymap('{0:.2f}'.format)
    
    return {'AD_results':AD_results, 
            'ScrewPress_results': ScrewPress_results, 
            'Filtration_results': filtration_module_results,
            'FBR_results': FBR_module_results,
            'CSTR_results': CSTR_module_results,
            'results_summary' : results_summary,
            'economic_results_summary' : economic_results_summary,
            }







#pd.DataFrame.from_dict({(i): AD_fc[i] for i in AD_fc.keys()},  orient='index')

#def main_function(F_ini, product):       
    #from filtration_module import filtration_module
    #from centrifugation_module import centrifugation_module
    #from FBR_wo_dryer_module import FBR_module
    #from CSTR_wt_dryer_module import CSTR_module
    
    #products_dict = {'filtration':'nop',
                #'centrifugation':'nop',
                #'FBR':'str',
                #'CSTR':'str'}
    
    #filtration_results = filtration_module(F_ini)
    #centrifugation_results = centrifugation_module(F_ini)
    #FBR_results = FBR_module(F_ini)
    #CSTR_results = CSTR_module(F_ini)
    
    #technologies = {'filtration':filtration_results['tech'], 
                    #'centrifugation':centrifugation_results['tech'], 
                    #'FBR':FBR_results['tech'], 
                    #'CSTR':CSTR_results['tech']}  
        
    #benefits={'filtration':filtration_results['benefits'], 
              #'centrifugation':centrifugation_results['benefits'], 
              #'FBR':FBR_results['benefits'], 
              #'CSTR':CSTR_results['benefits']}
    
    #if product == '':  
        #benefits_selection = max(benefits.values())
    ##    tech_selected = technologies[benefits.index(max(benefits))]
        #for i_tech, i_benefit in benefits.items():
            #if i_benefit == max(benefits.values()):
                #tech_selected = technologies[i_tech]
                
    #else: #product == 'nop':
        #for i_tech, i_product in products_dict.items():
            #if i_product != product:
                #del technologies[i_tech]
                #del benefits[i_tech]
                
        #benefits_selection = max(benefits.values())
        #for i_tech, i_benefit in benefits.items():
            #if i_benefit == max(benefits.values()):
                #tech_selected = technologies[i_tech]
                    
##    else:
##        benefits_selection = 'ERROR'
##        tech_selected = 'ERROR'

##    development returns
##    print(benefits)
##    print(benefits_selection)
##    print(tech_selected)
##    print(product)
    
    #return {'tech':tech_selected, 'benefits':benefits_selection}

    
    
    
    
