from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('references/', views.references, name='references'),
    path('techs/', views.TechListView.as_view(), name='techlist'), #This view (as_view()) format is because it will be implemented as a class
    #path('techs/<int:pk>', view.TechDetailView.as_view(), name='techdetails'),
    #re_path(r'^techs/(?P<stub>[-\w]+)$', views.TechDetailView.as_view(), name='tech-detail'),
    re_path(r'^techs/(?P<pk>\d+)$', views.TechDetailView.as_view(), name='tech-detail'), #Regular path option
    
    #Passing additional options in your URL maps    
    #path('url/', views.my_reused_view, {'my_template_name': 'some_path'}, name='aurl'),
    #path('anotherurl/', views.my_reused_view, {'my_template_name': 'another_path'}, name='anotherurl'),
]

urlpatterns += [
    path('user-input/', views.userinput, name='userinput'),
    path('model-output/', views.modeloutput, name='modeloutput'),
    path('design-output/', views.designoutput, name='designoutput'),
    path('indicators/', views.indicators, name='indicators'),
    path('economic-eval/', views.economic_eval, name='economic_eval'),
    path('results-index/', views.resultsindex, name='resultsindex')
]
