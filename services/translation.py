from modeltranslation.translator import register,TranslationOptions
from .models import TechnologyService, InfrastructureService, InnovationService

@register(TechnologyService)
class TechnologyServiceTranslationOption(TranslationOptions):
    fields = ('title',"content")

@register(InfrastructureService)
class InfrastructureServiceTranslationOption(TranslationOptions):
    fields = ('title', 'content' )

@register(InnovationService)
class InnovationServiceTranslationOption(TranslationOptions):
    fields = ('title', 'content')


