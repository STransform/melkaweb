from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import NewsArticle
from modeltranslation.translator import translator
from modeltranslation import settings
from django.conf import settings as proj_settings

from modeltranslation.utils import (
    get_translation_fields,

)

def get_label(field, lang):
    try:
        name = proj_settings.LANGS[lang] 
    except: 
        name = ""
    return f"{field} {name}"

class NewsArticleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)
        self.trans_opts = translator.get_options_for_model(self.Meta.model)


    def _patch_trans_fields(self):
        fields_new = {}
        for field, form in self.fields.items():
            if field in self.trans_opts.fields:
                # remove original field from self.fields
                translation_fields = get_translation_fields(field)
                
                for trans_field in translation_fields:
                    if hasattr(self.Meta.model, trans_field):
                        lang = trans_field.replace(f"{field}_","")
                        form.label = get_label(field, lang)
                        fields_new.update({trans_field:form})
            else:
                fields_new.update({field:form})

        self.fields = fields_new
            
    class Meta:
        model = NewsArticle
        fields = ['title', 'created_by', 'content', 'featured_image', 'minutes_read', 'news_category']
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control', 'label':'Title'}),
            'created_by':forms.TextInput(attrs={'class':'form-control', 'label':'created_by'}),
            'content':forms.Textarea(attrs={'class':'form-control', 'label':'Your Content'}),
        }
