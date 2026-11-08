from django.shortcuts import render, redirect
from django.views import View
from .models import *
from django.db.models.base import ModelBase

 
def technology_service(request): # Render about us page 
    technology_data = TechnologyService.objects.first()
    technology_service = TechnologyService.objects.all()
    context = {
        'technology_data': technology_data,
        'technology_service': technology_service,
    }

    return render(request, 'front/technology.html', context)
 
def technology_service(request): # Render structure page 
    technology_data = TechnologyService.objects.first()
    return render(request, 'front/technology.html', {'technology_data': technology_service})


def infrastructure_service(request): # Render structure page 
    infrastructure_data = InfrastructureService.objects.first()
    return render(request, 'front/infrastructure.html', {'infrastructure_data': infrastructure_service})

def innovation_service(request): # Render structure page 
    innovation_data = InnovationService.objects.first()
    return render(request, 'front/innovation.html', {'innovation_data': innovation_service})

    

