from django.shortcuts import render, redirect
from django.views import View
from .models import *
from django.db.models.base import ModelBase

 
def about(request): # Render about us page 
    about_data = About.objects.first()
    team_members = TeamMember.objects.all()
    context = {
        'about_data': about_data,
        'team_members': team_members, 'about_page': True,
    }

    return render(request, 'front/about.html', context)


def bureau_structure(request): # Render structure page 
    structure_data = BureauStructure.objects.first()
    return render(request, 'front/structure.html', {'structure_data': structure_data})


class ServicesPage(View): # Render service page 
    def get(self, request, **kwargs):
        services = Service.objects.all()
        return render(request, "front/services.html", {'services':services, 
        'service_page': True, 'page_title': 'Our Services', 'page_subtitle': 'Delivering impactful solutions that turn your vision into reality.'})


class TechnologyPage(View): # Render technology page 
    def get(self, request, **kwargs):
        technologies = Technology.objects.all()
        services = []

        for tech in technologies:
            services.append({
                "image_url": tech.image.url if tech.image else None,
                "content": tech.content,
                "title": tech.title
            })
            
        return render(request, "front/services.html", {'services':services, 
        'service_page': True, 'page_title': 'Core software development services', 
                                                       'page_subtitle': 'Empowering businesses with tailored digital strategies and tools.'})

class InfrastructurePage(View): # Render infrastructure page 
    def get(self, request, **kwargs):
        infrastructures = Infrastructure.objects.all()
        services = []

        for infrastructure in infrastructures:
            services.append({
                "image_url": infrastructure.infr_image.url if infrastructure.infr_image else None,
                "content": infrastructure.infr_content,
                "title": infrastructure.infr_title
            })
            
        return render(request, "front/services.html", {'services':services,
        'service_page': True, 'page_title': 'Enterprise & Business solutions', 'page_subtitle': 'Building scalable, secure, and efficient technology foundations.'})

class InnovationPage(View): # Render innovation page 
    def get(self, request, **kwargs):
        innovations = Innovation.objects.all()
        services = []

        for innovation in innovations:
            services.append({
                "image_url": innovation.invn_image.url if innovation.invn_image else None,
                "content": innovation.invn_content,
                "title": innovation.invn_title
            })
            
        return render(request, "front/services.html", {'services':services,
        'service_page': True, 'page_title': 'Web & Digital services', 'page_subtitle': 'Transforming ideas into impactful, future-ready solutions.'})
    
class CompanyValuesPage(View): # Render values page 
    def get(self, request, **kwargs):
        values = CompanyValues.objects.all()
        return render(request, "front/company_values.html", {'values':values,
        'about_page': True,})
class VisionMissionPage(View): # Render service page 
    def get(self, request, **kwargs):
        vision_mission = VisionMission.objects.all()
        return render(request, "front/vision_mission.html", {'vision_mission':vision_mission})

class VisionPage(View): # Render service page 
    def get(self, request, **kwargs):
        vision = Vision.objects.all()
        return render(request, "front/vision.html", {'vision':vision})
class OtechExcellencePage(View): # Render service page 
    def get(self, request, **kwargs):
        otech_excellence = OtechExcellence.objects.all()
        return render(request, "front/otech_excellence.html", {'otech_excellence':otech_excellence})
class WhatPeopleSaysPage(View): # Render service page 
    def get(self, request, **kwargs):
        people_saying = WhatPeopleSays.objects.all()
        return render(request, "front/people_saying.html", {'people_saying':people_saying})
class AboutOtechFooterPage(View): # Render service page 
    def get(self, request, **kwargs):
        about_footer = AboutOtechFooter.objects.all()
        return render(request, "front/about_footer.html", {'about_footer':about_footer})
    
class ElevatingSkillsPage(View): # Render service page 
    def get(self, request, **kwargs):
        elevating_skills = ElevatingSkills.objects.all()
        return render(request, "front/elevating_skills.html", {'elevating_skills':elevating_skills})

class OurPartnersPage(View): # Render service page 
    def get(self, request, **kwargs):
        our_partners = OurPartners.objects.all()
        return render(request, "front/our_partners.html", {'our_partners':our_partners, 'about_page': True,})
