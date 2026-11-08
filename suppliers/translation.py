from .models import *
from modeltranslation.translator import TranslationOptions, register

@register(Supplier)
class NewsCategoryTO(TranslationOptions):
    fields = ("company_name","legal_form","nationality","area_of_business" )
