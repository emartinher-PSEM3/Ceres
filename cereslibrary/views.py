from django.shortcuts import render, get_object_or_404, render_to_response
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse
from collections import OrderedDict
#from string import ascii_lowercase
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6
import pandas as pd
import numpy as np
pd.set_option('display.float_format', '{:.2E}'.format)

# Create your views here.

from cereslibrary.models import Tech, UserInputData#, Product
from cereslibrary.techmodels.economic_parameters_module import ec_param

def index(request):
        """View function for home page of site."""
        
        #Generate counts
        num_tech = Tech.objects.all().count()
        num_techs_wt_product = Tech.objects.filter(product__exact='str').count() + Tech.objects.filter(product__exact='otr').count()
        num_techs_wo_product = Tech.objects.filter(product__exact='nop').count()
        #num_techs_wt_product = Product.objects.filter(name__exact='Struvite').count() + Product.objects.filter(name__exact='Other').count()
        #num_techs_wo_product = Product.objects.filter(name__exact='No product').count()
        
        context = {
            'num_tech' : num_tech,
            'num_techs_wt_product' : num_techs_wt_product,
            'num_techs_wo_product' : num_techs_wo_product,
        }
        # Render the HTML template index.html with the data in the context variable
        return render(request, 'index.html', context=context)


class TechListView(generic.ListView):
    model = Tech
    paginate_by = 10
    #context_object_name = 'technologies_list' # your own name for the list as a template variable
    #queryset = Tech.objects.filter(product__exact='str')
    #template_name = 'path....'
    
    #def get_queryset(self):
        #return Tech.objects.filter(product__exact='str')
        
    #def get_context_data(self, **kwargs):
        ## Call the base implementation first to get the context
        #context = super(TechListView, self).get_context_data(**kwargs) #TechDetails is a superclass
        ## Create any data and add it to the context
        #context['some data'] = 'Thisis just some data'
        #return context # return the new (updated) context.
        
class TechDetailView(generic.DetailView):
    model = Tech
    
#Manually it will be:
#def book_detail_view(request, primary_key):
    #try:
        #book = Book.objects.get(pk=primary_key)
    #except Book.DoesNotExist:
        #raise Http404('Book does not exist')
        
    #OR this shortcut
    #book = get_object_or_404(Book, pk=primary_key)
    
    #return render(request, 'catalog/book_detail.html', context={'book': book})


def references(request):
    return render(request, 'cereslibrary/references.html', context=None)


from cereslibrary.forms import UserInputForm

import os, sys, inspect
# Use this if you want to include modules from a subfolder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"techmodels")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)
cmd_subfolder2 = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"GIS")))
if cmd_subfolder2 not in sys.path:
    sys.path.insert(0, cmd_subfolder2)
    
#from budgettest import budget_test
from cereslibrary.techmodels.main_v2W import main_function
from cereslibrary.GIS.GIS_retrieval import GIS_retrieval_module
from cereslibrary.GIS.GIS_maps import GIS_maps_module


def userinput(request):
    #input_instance = UserInputForm.get.objects(data=data)
    
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = UserInputForm(request.POST)
        
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            #UserInputData.user_budget = form.cleaned_data['user_budget']
            #UserInputData.product = form.cleaned_data['product']
            #UserInputData.manure_composition = form.cleaned_data['manure_composition']
            #UserInputData.user_budget = form.cleaned_data['user_budget']
            
            UserInputData.facility_size = form.cleaned_data['facility_size']
            UserInputData.AD_decision = form.cleaned_data['AD_decision']
            UserInputData.latitude = form.cleaned_data['latitude']
            UserInputData.longitude = form.cleaned_data['longitude']
            UserInputData.discharge_mode = form.cleaned_data['discharge_mode']
            UserInputData.discount_rate = form.cleaned_data['discount_rate']
            #results = main_function(form.cleaned_data['facility_size'])
            #Tech.title = results['AD_results']['tech']
            #Tech.investment_cost = results['AD_results']['AD_investment_cost']
            #Tech.operation_cost = results['AD_results']['AD_operation_cost']
            
            #Tech.fc = results['AD_results']['fc']
            # redirect to a new URL
            # redirect to a new URL:
            #return HttpResponseRedirect(reverse('modeloutput') )
            return HttpResponseRedirect(reverse('resultsindex') )

    
    
    # If this is a GET (or any other method) create the default form.
    else:
        form = UserInputForm(initial={'budget':0.0})
        
    context = {
            'form':form,
    }
    
    return render (request, 'cereslibrary/user-input.html', context=context)



def modeloutput(request):
    """View function for home page of site."""
    
    results = main_function(UserInputData.facility_size, UserInputData.AD_decision)
    
    #Model output
    #budget_output = UserInputData.user_budget
    #context = None
    
    #AD
    if UserInputData.AD_decision:
        tech_AD = results['AD_results']['tech']
        investment_cost_AD = results['AD_results']['investment_cost']
        #operation_cost_AD = results['AD_results']['operation_cost_2016_amortized']
        operation_cost_AD = results['AD_results']['operation_cost_2016_non_amortized']
        fc_AD = OrderedDict(results['AD_results']['fc'])
        fc_DF_AD = pd.DataFrame.from_dict({(i): fc_AD[i] for i in fc_AD.keys()}, orient='index')
        fc_html_AD = fc_DF_AD.to_html(justify='center')
        AD_decision_AD = UserInputData.AD_decision
        
        context_AD = {
        #'budget_output' : budget_output,
        'tech_AD' : tech_AD,
        'investment_cost_AD' : investment_cost_AD,
        'operation_cost_AD' : operation_cost_AD,
        'fc_AD' : fc_html_AD,
        'AD_decision' : AD_decision_AD,
        #'product_output' : product_output,
        }
        
    if not UserInputData.AD_decision:
        context_AD = {'tech_AD' : 'AD no selected'}
    
    #Screw Press
    tech_SP = results['ScrewPress_results']['tech']
    investment_cost_SP = results['ScrewPress_results']['investment_cost']
    operation_cost_SP = results['ScrewPress_results']['operation_cost_2016_non_amortized']
    fc_SP = OrderedDict(results['ScrewPress_results']['fc'])
    fc_DF_SP = pd.DataFrame.from_dict({(i): fc_SP[i] for i in fc_SP.keys()}, orient='index')
    fc_html_SP = fc_DF_SP.to_html(justify='center')
    
    context_SP = {
        #'budget_output' : budget_output,
        'tech_SP' : tech_SP,
        'investment_cost_SP' : investment_cost_SP,
        'operation_cost_SP' : operation_cost_SP,
        'fc_SP' : fc_html_SP,
        #'AD_decision' : AD_decision_AD,
        #'product_output' : product_output,
        }
    
    #Filter
    tech_FI = results['Filtration_results']['tech']
    investment_cost_FI = results['Filtration_results']['investment_cost']
    operation_cost_FI = results['Filtration_results']['operation_cost_2016_non_amortized']
    fc_FI = OrderedDict(results['Filtration_results']['fc'])
    fc_DF_FI = pd.DataFrame.from_dict({(i): fc_FI[i] for i in fc_FI.keys()}, orient='index')
    fc_html_FI = fc_DF_FI.to_html(justify='center')
    investment_cost_status_FI    = results['Filtration_results']['investment_cost_status']
    operation_cost_status_FI     = results['Filtration_results']['operation_cost_status']
    
    recoved_P_FI                 = results['Filtration_results']['recoved_P']
    recoved_PO4_FI               = results['Filtration_results']['recoved_PO4']
    released_P_FI                = results['Filtration_results']['released_P']
    released_PO4_FI              = results['Filtration_results']['released_PO4']
    fraction_recoved_P_FI        = results['Filtration_results']['fraction_recoved_P']
    fraction_recoved_PO4_FI      = results['Filtration_results']['fraction_recoved_PO4']
    fraction_released_P_FI       = results['Filtration_results']['fraction_released_P']
    fraction_released_PO4_FI     = results['Filtration_results']['fraction_released_PO4']
    fraction_recoved_TP_FI       = results['Filtration_results']['fraction_recoved_TP']
    fraction_released_TP_FI      = results['Filtration_results']['fraction_released_TP']
    #filter_P_dict           = {**recoved_P, **recoved_PO4, **released_P, **released_PO4, **fraction_recoved_P, **fraction_recoved_PO4, **fraction_released_P, **fraction_released_PO4}
    filter_P_dict           = {'recoved_P':recoved_P_FI, 
                               'recoved_PO4':recoved_PO4_FI, 
                               'released_P':released_P_FI, 
                               'released_PO4':released_PO4_FI, 
                               'fraction_recoved_P':format(fraction_recoved_P_FI, '.2f'), 
                               'fraction_recoved_PO4':format(fraction_recoved_PO4_FI, '.2f'), 
                               'fraction_released_P':format(fraction_released_P_FI, '.2f'), 
                               'fraction_released_PO4':format(fraction_released_PO4_FI, '.2f'),
                               'fraction_recoved_TP':format(fraction_recoved_TP_FI, '.2f'), 
                               'fraction_released_TP':format(fraction_released_TP_FI, '.2f'),
                               }
    
    p_DF_FI                 = pd.DataFrame.from_dict(filter_P_dict, orient='index', columns=['Filtration'])
    p_html_FI               = p_DF_FI.to_html(justify='center')
    
    context_FI = {
        'tech_FI' : tech_FI,
        'investment_cost_FI' : investment_cost_FI,
        'operation_cost_FI' : operation_cost_FI,
        'fc_FI' : fc_html_FI,
        'investment_cost_status_FI' : investment_cost_status_FI,
        'operation_cost_status_FI'  : operation_cost_status_FI,
        'p_FI' : p_html_FI
        }
    
    #FBR
    tech_FBR = results['FBR_results']['tech']
    investment_cost_FBR = results['FBR_results']['investment_cost']
    operation_cost_FBR = results['FBR_results']['operation_cost_2016_non_amortized']
    fc_FBR = OrderedDict(results['FBR_results']['fc'])
    fc_DF_FBR = pd.DataFrame.from_dict({(i): fc_FBR[i] for i in fc_FBR.keys()}, orient='index')
    fc_html_FBR = fc_DF_FBR.to_html(justify='center')
    
    recovered_P_FBR             = results['FBR_results']['recovered_P']
    recovered_PO4_FBR           = results['FBR_results']['recovered_PO4']
    released_P_FBR              = results['FBR_results']['released_P']
    released_PO4_FBR            = results['FBR_results']['released_PO4']
    fraction_recoved_P_FBR      = results['FBR_results']['fraction_recoved_P']
    fraction_recoved_PO4_FBR    = results['FBR_results']['fraction_recoved_PO4']
    fraction_released_P_FBR     = results['FBR_results']['fraction_released_P']
    fraction_released_PO4_FBR   = results['FBR_results']['fraction_released_PO4']
    fraction_recoved_TP_FBR     = results['FBR_results']['fraction_recoved_TP']
    fraction_released_TP_FBR    = results['FBR_results']['fraction_released_TP']
    FBR_P_dict              = {'recovered_P':recovered_P_FBR, 
                               'recovered_PO4':recovered_PO4_FBR, 
                               'released_P':released_P_FBR, 
                               'released_PO4':released_PO4_FBR, 
                               'fraction_recoved_P':format(fraction_recoved_P_FBR, '.2f'), 
                               'fraction_recoved_PO4':format(fraction_recoved_PO4_FBR, '.2f'), 
                               'fraction_released_P':format(fraction_released_P_FBR, '.2f'), 
                               'fraction_released_PO4':format(fraction_released_PO4_FBR, '.2f'),
                               'fraction_recoved_TP':format(fraction_recoved_TP_FBR, '.2f'), 
                               'fraction_released_TP':format(fraction_released_TP_FBR, '.2f'),
                               }
    p_DF_FBR                    = pd.DataFrame.from_dict(FBR_P_dict, orient='index', columns=['FBR'])
    p_html_FBR                  = p_DF_FBR.to_html(justify='center')
    
    context_FBR = {
        'tech_FBR' : tech_FBR,
        'investment_cost_FBR' : investment_cost_FBR,
        'operation_cost_FBR' : operation_cost_FBR,
        'fc_FBR' : fc_html_FBR,
        'p_FBR' : p_html_FBR
        }
    
    #CSTR
    tech_CSTR = results['CSTR_results']['tech']
    investment_cost_CSTR = results['CSTR_results']['investment_cost']
    operation_cost_CSTR = results['CSTR_results']['operation_cost_2016_non_amortized']
    fc_CSTR = OrderedDict(results['CSTR_results']['fc'])
    fc_DF_CSTR = pd.DataFrame.from_dict({(i): fc_CSTR[i] for i in fc_CSTR.keys()}, orient='index')
    fc_html_CSTR = fc_DF_CSTR.to_html(justify='center')
    
    recovered_P_CSTR             = results['CSTR_results']['recovered_P']
    recovered_PO4_CSTR           = results['CSTR_results']['recovered_PO4']
    released_P_CSTR              = results['CSTR_results']['released_P']
    released_PO4_CSTR            = results['CSTR_results']['released_PO4']
    fraction_recoved_P_CSTR      = results['CSTR_results']['fraction_recoved_P']
    fraction_recoved_PO4_CSTR    = results['CSTR_results']['fraction_recoved_PO4']
    fraction_released_P_CSTR     = results['CSTR_results']['fraction_released_P']
    fraction_released_PO4_CSTR   = results['CSTR_results']['fraction_released_PO4']
    fraction_recoved_TP_CSTR     = results['CSTR_results']['fraction_recoved_TP']
    fraction_released_TP_CSTR   = results['CSTR_results']['fraction_released_TP']
    CSTR_P_dict              = {'recovered_P':recovered_P_CSTR, 
                               'recovered_PO4':recovered_PO4_CSTR, 
                               'released_P':released_P_CSTR, 
                               'released_PO4':released_PO4_CSTR, 
                               'fraction_recoved_P':format(fraction_recoved_P_CSTR, '.2f'), 
                               'fraction_recoved_PO4':format(fraction_recoved_PO4_CSTR, '.2f'), 
                               'fraction_released_P':format(fraction_released_P_CSTR, '.2f'), 
                               'fraction_released_PO4':format(fraction_released_PO4_CSTR, '.2f'),
                               'fraction_recoved_TP':format(fraction_recoved_TP_CSTR, '.2f'), 
                               'fraction_released_TP':format(fraction_released_TP_CSTR, '.2f'),
                               }
    p_DF_CSTR                    = pd.DataFrame.from_dict(CSTR_P_dict, orient='index', columns=['CSTR'])
    p_html_CSTR                  = p_DF_CSTR.to_html(justify='center')
    
    context_CSTR = {
        'tech_CSTR' : tech_CSTR,
        'investment_cost_CSTR' : investment_cost_CSTR,
        'operation_cost_CSTR' : operation_cost_CSTR,
        'fc_CSTR' : fc_html_CSTR,
        'p_CSTR' : p_html_CSTR
        }
    
    
    #product_output = UserInputData.product
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'cereslibrary/modeloutput.html', context={**context_AD, **context_SP, **context_FI, **context_FBR, **context_CSTR})

def designoutput(request):
    results = main_function(UserInputData.facility_size, UserInputData.AD_decision)
    
    #Screw Press
    tech_SP     = results['ScrewPress_results']['tech']
    n_units_SP  = results['ScrewPress_results']['n_ScrewPress']
    size_SP     = round(results['ScrewPress_results']['ScrewPress_diameter'], 3)
    energy_SP   = round(results['ScrewPress_results']['power_kW_ScrewPress'], 3)
    
    context_SP = {
    'tech_SP'       : tech_SP,
    'n_units_SP'    : n_units_SP,
    'size_SP'       : size_SP,
    'energy_SP'     : energy_SP
    }
    #Filter
    tech_FI     = results['Filtration_results']['tech']
    n_units_FI  = results['Filtration_results']['n_filters']
    type_FI     = results['Filtration_results']['filter_type']
    media_FI    = results['Filtration_results']['filter_media']
    investment_cost_status_FI    = results['Filtration_results']['investment_cost_status']
    operation_cost_status_FI     = results['Filtration_results']['operation_cost_status']
    
    context_FI = {
    'tech_FI'                   : tech_FI,
    'n_units_FI'                : n_units_FI,
    'type_FI'                   : type_FI,
    'media_FI'                  : media_FI,
    'investment_cost_status_FI' : investment_cost_status_FI,
    'operation_cost_status_FI'  : operation_cost_status_FI
    }
    
    #FBR
    tech_FBR     = results['FBR_results']['tech']
    n_units_FBR  = results['FBR_results']['n_FBR']
    FBR_size     = results['FBR_results']['FBR_size']
    
    context_FBR = {
    'tech_FBR'                   : tech_FBR,
    'n_units_FBR'                : n_units_FBR,
    'FBR_size'                   : FBR_size
    }
    
    #CSTR
    tech_CSTR       = results['CSTR_results']['tech']
    n_units_CSTR    = results['CSTR_results']['n_CSTR']
    CSTR_size       = results['CSTR_results']['Reactor V']
    n_units_Clarifier    = results['CSTR_results']['n_Clarifier']
    Clarifier_size  = results['CSTR_results']['Clarifier V']
    n_units_BeltFilt    = results['CSTR_results']['n_BeltFilt']
    BeltFilt_size  = results['CSTR_results']['BeltFilt_area']
    n_units_ConveyorDryer    = results['CSTR_results']['n_ConveyorDryer']
    ConveyorDryer_size  = results['CSTR_results']['ConveyorDryer_area']
    
    context_CSTR = {
    'tech_CSTR'                   : tech_CSTR,
    'n_units_CSTR'                : n_units_CSTR,
    'CSTR_size'                   : CSTR_size,
    'n_units_Clarifier'           : n_units_Clarifier,
    'Clarifier_size'              : Clarifier_size,
    'n_units_BeltFilt'            : n_units_BeltFilt,
    'BeltFilt_size'               : BeltFilt_size,
    'n_units_ConveyorDryer'       : n_units_ConveyorDryer,
    'ConveyorDryer_size'          : ConveyorDryer_size,
    }
    
    return render(request, 'cereslibrary/designoutput.html', context={**context_SP, **context_FI, **context_FBR, **context_CSTR})
    
def resultsindex(request):
    return render(request, 'cereslibrary/results_index.html', context=None)
    

def indicators(request):
    results_GIS = GIS_retrieval_module(UserInputData.latitude, UserInputData.longitude)
    results = main_function(UserInputData.facility_size, UserInputData.AD_decision)
    discharge_mode = UserInputData.discharge_mode
    
    #Summary of results
    if UserInputData.AD_decision:
        results_summary         = results['results_summary']
        results_summary_html    = results_summary.to_html(justify='center')
    
    if not UserInputData.AD_decision:
        results_summary                                 = results['results_summary'].copy()
        results_summary.loc[['Anaerobic digestion'],:]  = ['NA', 'NA','NA','NA','NA','NA',]
        #results_summary                                 = results_summary.applymap('{0:.2f}'.format)
        results_summary_html                            = results_summary.to_html(justify='center')
    
    #economic_results_summary        = results['economic_results_summary'] 
    #economic_results_summary_html   = economic_results_summary.to_html(justify='center')
    
    context_results_summary = {
        'results_summary' : results_summary_html
        }
    
    
    #Emission limit
    P_emission_limit_dict   = {'direct':100, 'non_direct':50}
    P_emission_mode_dict    = {'direct':'directly in a waterbody', 'non_direct':'non-directly in a waterbody'}
    P_emission_limit        = P_emission_limit_dict[discharge_mode]
    P_emission_mode         = P_emission_mode_dict[discharge_mode]
    
    context_P_emission_limit = {
    'P_emission_limit'  :P_emission_limit,
    'P_emission_mode'   :P_emission_mode,
    }
    
    #GIS data
    TP_GIS          = results_GIS['TP_GIS']
    NH4_GIS         = results_GIS['NH4_GIS']
    HUC8ContPoint   = results_GIS['HUC8ContPoint']
    
    context_GIS = {
    'TP_GIS'                      : TP_GIS,
    'NH4_GIS'                     : NH4_GIS,
    'HUC8ContPoint'               : HUC8ContPoint,
    }
    
    #HUC8 eutrophiation risk
    eutrophication_risk_thresholds = [10, 20] #microg/L
    eutrophication_risk_standards = ['Low risk', 'Medium risk', 'High risk']
    
    if TP_GIS < eutrophication_risk_thresholds[0]:
        eutrophication_risk = eutrophication_risk_standards[0]
    elif eutrophication_risk_thresholds[0] < TP_GIS < eutrophication_risk_thresholds[1]:
        eutrophication_risk = eutrophication_risk_standards[1]
    elif TP_GIS > eutrophication_risk_thresholds[1]:
        eutrophication_risk = eutrophication_risk_standards[2]
        
    context_eutrophication_risk = {
        'eutrophication_risk' : eutrophication_risk
        }
    
    #Filter
    tech_FI                      = results['Filtration_results']['tech']
    recoved_P_FI                 = results['Filtration_results']['recoved_P']
    recoved_PO4_FI               = results['Filtration_results']['recoved_PO4']
    released_P_FI                = results['Filtration_results']['released_P']
    released_PO4_FI              = results['Filtration_results']['released_PO4']
    fraction_recoved_P_FI        = results['Filtration_results']['fraction_recoved_P']
    fraction_recoved_PO4_FI      = results['Filtration_results']['fraction_recoved_PO4']
    fraction_released_P_FI       = results['Filtration_results']['fraction_released_P']
    fraction_released_PO4_FI     = results['Filtration_results']['fraction_released_PO4']
    fraction_recoved_TP_FI       = results['Filtration_results']['fraction_recoved_TP']
    fraction_released_TP_FI      = results['Filtration_results']['fraction_released_TP']
    #filter_P_dict           = {**recoved_P, **recoved_PO4, **released_P, **released_PO4, **fraction_recoved_P, **fraction_recoved_PO4, **fraction_released_P, **fraction_released_PO4}
    filter_P_dict           = {'recovered_P':recoved_P_FI, 
                               'released_P':released_P_FI, 
                               'recovered_PO4':recoved_PO4_FI, 
                               'released_PO4':released_PO4_FI, 
                               'fraction_recovered_P':format(fraction_recoved_P_FI, '.2f'), 
                               'fraction_released_P':format(fraction_released_P_FI, '.2f'), 
                               'fraction_recovered_PO4':format(fraction_recoved_PO4_FI, '.2f'), 
                               'fraction_released_PO4':format(fraction_released_PO4_FI, '.2f'),
                               'fraction_recovered_TP':format(fraction_recoved_TP_FI, '.2f'), 
                               'fraction_released_TP':format(fraction_released_TP_FI, '.2f'),
                               }
    
    p_DF_FI                 = pd.DataFrame.from_dict(filter_P_dict, orient='index', columns=['Filtration'])
    p_html_FI               = p_DF_FI.to_html(justify='center')
    
    context_FI = {
        'p_FI' : p_html_FI
        }
    
    #FBR
    tech_FBR                    = results['FBR_results']['tech']
    recovered_P_FBR             = results['FBR_results']['recovered_P']
    recovered_PO4_FBR           = results['FBR_results']['recovered_PO4']
    released_P_FBR              = results['FBR_results']['released_P']
    released_PO4_FBR            = results['FBR_results']['released_PO4']
    fraction_recoved_P_FBR      = results['FBR_results']['fraction_recoved_P']
    fraction_recoved_PO4_FBR    = results['FBR_results']['fraction_recoved_PO4']
    fraction_released_P_FBR     = results['FBR_results']['fraction_released_P']
    fraction_released_PO4_FBR   = results['FBR_results']['fraction_released_PO4']
    fraction_recoved_TP_FBR     = results['FBR_results']['fraction_recoved_TP']
    fraction_released_TP_FBR    = results['FBR_results']['fraction_released_TP']
    FBR_P_dict              = {'recovered_P':recovered_P_FBR, 
                               'released_P':released_P_FBR, 
                               'recovered_PO4':recovered_PO4_FBR, 
                               'released_PO4':released_PO4_FBR, 
                               'fraction_recovered_P':format(fraction_recoved_P_FBR, '.2f'), 
                               'fraction_released_P':format(fraction_released_P_FBR, '.2f'),
                               'fraction_recovered_PO4':format(fraction_recoved_PO4_FBR, '.2f'), 
                               'fraction_released_PO4':format(fraction_released_PO4_FBR, '.2f'),
                               'fraction_recovered_TP':format(fraction_recoved_TP_FBR, '.2f'), 
                               'fraction_released_TP':format(fraction_released_TP_FBR, '.2f'),
                               }
    p_DF_FBR                    = pd.DataFrame.from_dict(FBR_P_dict, orient='index', columns=['FBR'])
    p_html_FBR                  = p_DF_FBR.to_html(justify='center')
    
    context_FBR = {
        'p_FBR' : p_html_FBR
        }
    
    #CSTR
    tech_CSTR                    = results['CSTR_results']['tech']
    recovered_P_CSTR             = results['CSTR_results']['recovered_P']
    recovered_PO4_CSTR           = results['CSTR_results']['recovered_PO4']
    released_P_CSTR              = results['CSTR_results']['released_P']
    released_PO4_CSTR            = results['CSTR_results']['released_PO4']
    fraction_recoved_P_CSTR      = results['CSTR_results']['fraction_recoved_P']
    fraction_recoved_PO4_CSTR    = results['CSTR_results']['fraction_recoved_PO4']
    fraction_released_P_CSTR     = results['CSTR_results']['fraction_released_P']
    fraction_released_PO4_CSTR   = results['CSTR_results']['fraction_released_PO4']
    fraction_recoved_TP_CSTR     = results['CSTR_results']['fraction_recoved_TP']
    fraction_released_TP_CSTR    = results['CSTR_results']['fraction_released_TP']
    CSTR_P_dict              = {'recovered_P':recovered_P_CSTR, 
                               'released_P':released_P_CSTR, 
                               'recovered_PO4':recovered_PO4_CSTR,
                               'released_PO4':released_PO4_CSTR, 
                               'fraction_recovered_P':format(fraction_recoved_P_CSTR, '.2f'), 
                               'fraction_released_P':format(fraction_released_P_CSTR, '.2f'), 
                               'fraction_recovered_PO4':format(fraction_recoved_PO4_CSTR, '.2f'), 
                               'fraction_released_PO4':format(fraction_released_PO4_CSTR, '.2f'),
                               'fraction_recovered_TP':format(fraction_recoved_TP_CSTR, '.2f'), 
                               'fraction_released_TP':format(fraction_released_TP_CSTR, '.2f'),
                               }
    p_DF_CSTR                    = pd.DataFrame.from_dict(CSTR_P_dict, orient='index', columns=['CSTR'])
    p_html_CSTR                  = p_DF_CSTR.to_html(justify='center')
    
    context_CSTR = {
        'p_CSTR' : p_html_CSTR
        }
    
    p_superDF_P     = pd.concat([p_DF_FI, p_DF_FBR, p_DF_CSTR], ignore_index=False, axis=1)
    p_superDFhtml_P = p_superDF_P.to_html(justify='center')
    context_P = {
        'resultsP' : p_superDFhtml_P
        }
    
    #p = figure(plot_width = 400, plot_height = 400) 
  
    ## add a circle renderer with 
    ## size, color and alpha 
    #p.circle([1, 2, 3, 4, 5], [4, 7, 1, 6, 3], size = 10, color = "navy", alpha = 0.5) 
    
    #plot = figure()
    #plot.circle([1,2], [3,4])
    #script, div = components(plot, CDN)
    
    p = figure(plot_width = 400, plot_height = 400) 
  
    # add a circle renderer with 
    # size, color and alpha 
    p.line([1, 2, 3, 4, 5], [4, 7, 1, 6, 3])
    script, div = components(p)

    context_bokeh = {"script": script, "div": div}
    
    return render(request, 'cereslibrary/indicators.html', context={**context_results_summary, **context_P_emission_limit, **context_eutrophication_risk, **context_GIS,**context_P, **context_bokeh})

def economic_eval(request):
    
    results = main_function(UserInputData.facility_size, UserInputData.AD_decision)
    discount_rate = UserInputData.discount_rate/100
    
    #economic_results_summary
    if UserInputData.AD_decision:
        economic_results_summary        = results['economic_results_summary'] 
        economic_results_summary_html    = economic_results_summary.to_html(justify='center')
    
    if not UserInputData.AD_decision:
        economic_results_summary                                    = results['economic_results_summary'] 
        economic_results_summary.loc[['Anaerobic digestion'],:]     = np.nan
        #results_summary                                            = results_summary.applymap('{0:.2f}'.format)
        economic_results_summary_html                               = economic_results_summary.to_html(justify='center')
    
    #economic_results_summary        = results['economic_results_summary'] 
    #economic_results_summary_html   = economic_results_summary.to_html(justify='center')
    
    context_economic_results_summary = {
        'economic_results_summary' : economic_results_summary_html
        }
    
    
    #Plot economic_results_summary
    techs = list(economic_results_summary.index.array)
    parameters = list(economic_results_summary.columns.array)
    
    
    x = [ (tech, parameter) for tech in techs for parameter in parameters ]
    #Explanation
    #df = pd.DataFrame({'c1':[4,2,8],'c2':[8,7,9]}, index=['a','b','c'])
        #c1  c2
    #a   4   8
    #b   2   7
    #c   8   9
    #sum([df[x].values.tolist() for x in df.columns],[])
    #[4, 2, 8, 8, 7, 9]
    counts = sum([economic_results_summary.loc[x].values.tolist() for x in economic_results_summary.index],[])
    economic_results_source = ColumnDataSource(data=dict(x=x, counts=counts))
    
    palette = ["#c9d9d3", "#718dbf", "#e84d60"]
    
    p = figure(x_range=FactorRange(*x), plot_height=650, title="Nutrient recovery techlonogies costs", 
           toolbar_location=None, tools="hover", tooltips="@x: @counts USD",)
    
    p.vbar(x='x', top='counts', width=0.9, source=economic_results_source, line_color="white",
       fill_color=factor_cmap('x', palette=palette, factors=parameters, start=1, end=2))
    
    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = np.pi/2
    
    script_economic_results_summary, div_economic_results_summary = components(p)
    
    #economic_results_source = ColumnDataSource(dict(x=list(economic_results_summary.index.array), top=economic_results_summary['Equipment_costs']))
    #p = figure(x_range=list(economic_results_summary.index.array), plot_height=350, toolbar_location=None, tools="hover", tooltips="@index: @Equipment_cost USD",
               #title="Nutrient recovery techlonogies equipment cost",)
    #p.vbar(x='index', top='Equipment_cost', width=0.9, source=economic_results_summary, line_color='white', legend='index', fill_color=factor_cmap('index', palette=Spectral3, factors=list(economic_results_summary.index.array)))
    #script_economic_results_summary, div_economic_results_summary = components(p)

    context_bokeh_economic_results_summary = {"script_economic_results_summary": script_economic_results_summary, "div_economic_results_summary": div_economic_results_summary}
    
    
    #NPV calculation
    topology = pd.read_csv('cereslibrary/techmodels/topology/topology.csv', sep=",", index_col=0, header=0)
    
    if UserInputData.AD_decision:
        topology_subset = topology[topology.index.str.contains("AD") == True]
        
    if not UserInputData.AD_decision:
        topology_subset = topology[topology.index.str.contains("AD") == False]
    
    arrangements = list(topology_subset.index.array)
    technologies = list(topology_subset.columns.array)
    topologies_dict = dict()
    cash_inflow_dict = dict()
    cash_outflow_dict = dict()
    cash_netflow_dict = dict()
    npv_dict = dict()
    npv_summary_dict = dict()
    for i in arrangements:
        tech_list=[]
        investment_cost_list=[]
        cash_inflow_list=[]
        cash_outflow_list=[]
        for ii in technologies:
            val = int(topology_subset.loc[i, ii])
            if val == 1:
                tech_list.append(ii)
                investment_cost_list.append(float(economic_results_summary.loc[ii,'Equipment_cost']))
                cash_inflow_list.append(float(economic_results_summary.loc[ii,'Input cash']))
                cash_outflow_list.append(float(economic_results_summary.loc[ii,'Operation cost non amortized']))
        topologies_dict[i] = tech_list
        cash_inflow_dict[i] = sum(cash_inflow_list)
        cash_outflow_dict[i] = sum(cash_outflow_list)
        cash_netflow_dict[i] = sum(cash_inflow_list)-sum(cash_outflow_list)
        #npv_dict[i] = np.npv(ec_param['discount_rate'], [-sum(investment_cost_list)]+[sum(cash_outflow_list)]*int(ec_param['plant_lifetime']))
        npv_dict[i] = np.npv(discount_rate, [-sum(investment_cost_list)]+[sum(cash_outflow_list)]*int(ec_param['plant_lifetime']))
        npv_summary_dict[i] = [sum(cash_inflow_list), sum(cash_outflow_list), sum(cash_inflow_list)-sum(cash_outflow_list), npv_dict[i]]
        
    NPV_summary = pd.DataFrame.from_dict(npv_summary_dict, orient='index', 
                           columns=['Cash inflow', 'Cash outflow', 'Cash netflow', 'NPV'])
    
    NPV_summary_html    = NPV_summary.to_html(justify='center')
    
    context_NPV_summary = {
        'discount_rate' : discount_rate*100,
        'NPV_summary' : NPV_summary_html
        }
    
    
    #techs = list(economic_results_summary.index.array)
    #npv_dict = dict()
    
    #for i in techs:
        #net_cashflows   = float(economic_results_summary.loc[i,'Input cash']) - float(economic_results_summary.loc[i,'Operation cost non amortized'])
        #npv             = np.npv(ec_param['discount_rate'], [net_cashflows]*int(ec_param['plant_lifetime'])) #ec_param['plant_lifetime']
        #npv_dict[i]        = npv
    
    #economic_results_summary['NPV'] = economic_results_summary.index.map(npv_dict)
    #economic_results_summary_html    = economic_results_summary.to_html(justify='center')
    
    #context_economic_results_summary = {
        #'economic_results_summary' : economic_results_summary_html
        #}
    
    #npv_dict = {key:(np.npv(ec_param['discount_rate'], np.array(list(economic_results_summary.loc[key,'Input cash'])*ec_param['plant_lifetime']))) for key in techs}
    
    #investments = np.array(economic_results_summary.loc[:,'Investment cost'])
    #outflow     = np.array(economic_results_summary.loc[:,'Operation cost non amortized'])
    #inflow      = np.array(economic_results_summary.loc[:,'Input cash'])
    
    #net_cashflows = inflow - outflow
    
    #npv             = np.npv(discountRate, cashflows)
    
    
    #Plot NPV
    #techs = list(economic_results_summary.index.array)
    #parameters = list(economic_results_summary.columns.array)
    
    
    #x = [ (tech, parameter) for tech in techs for parameter in parameters ]
    #Explanation
    #df = pd.DataFrame({'c1':[4,2,8],'c2':[8,7,9]}, index=['a','b','c'])
        #c1  c2
    #a   4   8
    #b   2   7
    #c   8   9
    #sum([df[x].values.tolist() for x in df.columns],[])
    #[4, 2, 8, 8, 7, 9]
    #counts = sum([economic_results_summary.loc[x].values.tolist() for x in economic_results_summary.index],[])
    #economic_results_source = ColumnDataSource(data=dict(x=x, counts=counts))
    
    #palette = ["#c9d9d3", "#718dbf", "#e84d60"]
    
    #p = figure(x_range=FactorRange(*x), plot_height=650, title="Nutrient recovery techlonogies costs", 
           #toolbar_location=None, tools="hover", tooltips="@x: @counts USD",)
    
    #p.vbar(x='x', top='counts', width=0.9, source=economic_results_source, line_color="white",
       #fill_color=factor_cmap('x', palette=palette, factors=parameters, start=1, end=2))
    
    #p.y_range.start = 0
    #p.x_range.range_padding = 0.1
    #p.xaxis.major_label_orientation = np.pi/2
    
    #script_economic_results_summary, div_economic_results_summary = components(p)
    
    #economic_results_source = ColumnDataSource(dict(x=list(economic_results_summary.index.array), top=economic_results_summary['Equipment_costs']))
    palette = ["#c9d9d3", "#718dbf", "#e84d60"]
    p_NPV = figure(x_range=list(NPV_summary.index.array), plot_height=350, toolbar_location=None, tools="hover", tooltips="@index: @NPV USD",
               title="NPV for nutrient recovery topologies",)
    p_NPV.vbar(x='index', top='NPV', width=0.7, source=NPV_summary, line_color='white', legend='index', fill_color=factor_cmap('index', palette=palette, factors=list(NPV_summary.index.array)))
    p_NPV.legend.orientation = "vertical"
    p_NPV.legend.location = "bottom_right"
    p_NPV.legend.background_fill_alpha = 0
    script_NPV_summary, div_NPV_summary = components(p_NPV)

    context_bokeh_NPV_summary = {"script_NPV_summary": script_NPV_summary, "div_NPV_summary": div_NPV_summary}
    
    
    
    return render(request, 'cereslibrary/economic_eval.html', context={**context_economic_results_summary, **context_NPV_summary, **context_bokeh_economic_results_summary, **context_bokeh_NPV_summary})
