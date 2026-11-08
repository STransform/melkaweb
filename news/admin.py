from django.contrib import admin
from .models import NewsArticle, NewsCategory
from modeltranslation.admin import TranslationAdmin

# @admin.register(NewsArticle)
# class NewsArticleAdmin(TranslationAdmin):
#     list_display = ("title", "content")

# admin.site.register(NewsCategory)
