from .models import *
from modeltranslation.translator import TranslationOptions, register


@register(NewsCategory)
class NewsCategoryTO(TranslationOptions):
    fields = ("name", )

@register(NewsArticle)
class BlogTranslationOptions(TranslationOptions):
    fields = ("title", "content")
