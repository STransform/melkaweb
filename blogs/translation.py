from .models import *
from modeltranslation.translator import TranslationOptions, register

@register(Blog)
class BlogTO(TranslationOptions):
    fields = ("title","content")

@register(BlogCategory)
class BlogCategoryTO(TranslationOptions):
    fields = ("name",)

