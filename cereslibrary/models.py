from django.db import models
import django_tables2 as tables
from django import forms
from django.core.exceptions import ValidationError

# Create your models here.

#class Product(models.Model):
    #"""Model representing the obtained product"""
    #name = models.CharField(max_length=200, help_text='Expected product produced')
    
    #def __str__(self):
        #"""String for representing the Model object."""
        #return self.name
    
#class Product(models.Model):
    #"""Model representing the obtained product"""
    #PRD = (
        #('nop', 'No product'),
        #('str', 'Struvite'),
        #('otr','Other product'),
    #)
    
    #name = models.CharField(max_length=3,
                            #choices = PRD,
                            #blank = True,
                            #help_text='Expected product produced',
                            #)
    
    #def __str__(self):
        #"""String for representing the Model object."""
        #return self.name


from django.urls import reverse # Used to generate URLs by reversing the URL patterns

class Tech(models.Model):
    #Fields
    """Model representing a technology"""
    title = models.CharField(max_length=2000)
    description = models.TextField(max_length=1000, help_text='Brief description of the nutrients recovery technloogy')
    #product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, help_text='Select an expected product produced')
    PRD = (
        ('nop', 'No product'),
        ('str', 'Struvite'),
        ('otr','Other product'),
    )
    product = models.CharField(max_length=3,
                            choices = PRD,
                            blank = True,
                            default='nop',
                            help_text='Select an expected product produced',
                            )

    investment_cost = models.FloatField()
    operation_cost = models.FloatField()
    #fc = models.CharField(max_length=240)
    #payback = models.FloatField()
    #NPV = models.FloatField()
    benefits = models.FloatField()
    #PO4_reduction = models.FloatField()
    #NH4_reduction = models.FloatField()    
    
    #Methods
    def __str__(self):
        """String for representing the Model object."""
        return self.title
    
    def get_absolute_url(self):
        """Returns the url to access a detail record for this technology."""
        return reverse('tech-detail', args=[str(self.id)])
    
#class Discount_rate_dropdown(models.Model):
    #SEL = (
        #('def', 'Default'),
        #('cus', 'Custom'),
    #)
    
    #selection = models.CharField(max_length=3,
                            #choices = SEL,
                            #blank = True,
                            #default='def',
                            #help_text='Enter the discount rate for NPV'
                            #)
    #def __str__(self):
        #return self.selection
    
#class Discount_rate_custom(models.Model):
    #discount_rate_dropdown = models.ForeignKey(Discount_rate_dropdown, on_delete=models.CASCADE)
    #value = models.FloatField(default=0)

    #def __str__(self):
        #return self.value
   
class UserInputData(models.Model):
    facility_size = models.FloatField(default=0, help_text='Enter the number of animals of the facility')
    longitude = models.FloatField(default=0, help_text='Facility longitude')
    latitude = models.FloatField(default=0, help_text='Facility latitude')
    user_budget = models.FloatField(default=0, help_text='Enter a budget in USD')
    PRD = (
        ('nop', 'No product'),
        ('str', 'Struvite'),
        ('otr','Other product'),
        ('npf','NP fertilizer'),
        ('opf','P fertilizer'),
        ('onf','N fertilizer'),
    )
    product = models.CharField(max_length=3,
                            choices = PRD,
                            blank = True,
                            #default='nop',
                            help_text='Select an expected product produced',
                            )
    COMP = (
        ('def', 'Default'),
        ('cus', 'Custom'),
    )
    manure_composition = models.CharField(max_length=3,
                                          choices = COMP,
                                          default='def',
                                          blank = False,
                                          #help_text='It is not working yet')#'Enter the composition of the manure'   
                                          )
                                        
    CROP = (
        ('whe', 'Wheat'),
        ('hay', 'Hay'),
        ('bar','Barley'),
        ('cor','Corn'),
    )
    crop = models.CharField(max_length=3,
                            choices = CROP,
                            blank = True,
                            #default='nop',
                            help_text='Select an objective crop for the fertilizer',
                            )
    
    AD_decision = models.BooleanField(default=True) #default=False, null=True
    
    DISCHARGE = (
        ('direct', 'Directly in a waterbody'),
        ('non_direct', 'Non-directly in a waterbody'),
    )
    
    discharge_mode = models.CharField(max_length=10,
                            choices = DISCHARGE,
                            blank = False,
                            default='direct',
                            help_text='Select an discharge mode for after-treatment streams',
                            )
    
    
    #custom_discount_rate = models.BooleanField(default=True, help_text='Select discount rate for NPV')
    
    #discount_rate = models.FloatField(blank=True, null=True, help_text="(%). Only required if 'Custom discount rate' is selected.")
    
    #DEF, CUS = 'def', 'cus'
    
    SEL = (
        ('def', 'Default'),
        ('cus', 'Customized'),
    )
    
    customized_discount_rate = models.CharField(max_length=3,
                            choices = SEL,
                            blank = False,
                            default='def',
                            help_text='Select discount rate for NPV',
                            )
    
    discount_rate = models.FloatField(default=None, blank=True, null=True, help_text="(%). Only required if 'Customized discount rate' is selected.")
    
    def __str__(self):
        """String for representing the Model object."""
        return self.title
    
    #def __init__(self, data=None, *args, **kwargs):
        #super(UserInputData, self).__init__(data, *args, **kwargs)

        ## If 'Custom' is chosen, set send_date as required
        #if data and data.get('custom_discount_rate', None) == self.CUS:
            #self.fields['discount_rate'].required = True
    
        
    
    
    #def get_discharge_mode(self):
        #"""Returns the match name for a tag"""
        #return re.sub("\W+" , "", self.discharge_mode.lower())


#class DesignData(models.Model):
    #n_units
    #Size = models.FloatField()
    
    
    #def __str__(self):
        #"""String for representing the Model object."""
        #return self.title
