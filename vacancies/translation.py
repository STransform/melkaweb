from .models import *
from modeltranslation.translator import TranslationOptions, register

@register(Job)
class JobTO(TranslationOptions):
    fields = ("job_title","job_description", "skills","location")
 
