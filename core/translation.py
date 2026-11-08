from .models import Settings as WebSetting
from modeltranslation.translator import TranslationOptions, register

@register(WebSetting)
class WebSettingTO(TranslationOptions):
    fields = ("title", "address", "working_hours")


