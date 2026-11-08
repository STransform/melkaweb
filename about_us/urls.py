from django.urls import path
from .views import *  # Import the faqs_api view

urlpatterns = [
    path('about/', about, name='about'),
    path('services/', ServicesPage.as_view(), name='services'),
    path('bureau_structure/', bureau_structure, name='bureau_structure'),
    
    path('technology/', TechnologyPage.as_view(), name='technology'),
    path('infrastructure/', InfrastructurePage.as_view(), name='infrastructure'),
    path('innovation/', InnovationPage.as_view(), name='innovation'),
    path('companyvalues/', CompanyValuesPage.as_view(), name='company_values'),
    path('visionmission/', VisionMissionPage.as_view(), name='vision_mission'),
    path('vision/', VisionPage.as_view(), name='vision'),
    path('otech_excellence/', OtechExcellencePage.as_view(), name='otech_excellence'),
    path('people_saying/', WhatPeopleSaysPage.as_view(), name='people_saying'),
    path('about_footer/', AboutOtechFooterPage.as_view(), name='about_footer'),
    path('elevating_skills/', ElevatingSkillsPage.as_view(), name='elevating_skills'),
    path('our_partners/', OurPartnersPage.as_view(), name='our_partners'),
]

