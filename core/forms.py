import datetime
from typing import Any
from django import forms
from django.conf import settings
from django.forms import modelform_factory
from django.forms.fields import FileField, ImageField, DateField,DateTimeField, TimeField
from django.db.models import Model


ACCEPTABLE_DOCUMENT_TYPES_STR = '.doc, .docx, .pdf, .xlsx, .pptx'
ACCEPTABLE_IMAGE_TYPES_STR = '.png, .jpg, .jiff, .gif, .jpeg, .webp'

LANGS = {}
for item in getattr(settings, 'LANGUAGES'): LANGS[item[0]] = item[1]

class TranslatedForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        to_exclude = [] #empty list to store names of fields to be excluded
        lang_codes = LANGS.keys()
        for name, field in self.fields.items():
            # Created by is automatically taken from logged in user
            if name == "created_by": to_exclude.append(name) 

            # Control file types of uploaded files
            if isinstance(field, FileField):
                field.widget.attrs.update({'accept':ACCEPTABLE_DOCUMENT_TYPES_STR})

            # Control Image Types of uploaded contents
            if isinstance(field, ImageField):
                field.widget.attrs.update({'accept':ACCEPTABLE_IMAGE_TYPES_STR})

            # Add Calender selector for Date fields
            if isinstance(field, DateField) :
                self.fields[name] = forms.DateField(required=True, widget=forms.DateInput(attrs={'type':'text', 'class':"form-control flatpickr-input date"}))
            
            # Add Calender selector for Date time fields
            if isinstance(field, DateTimeField):
                self.fields[name] = forms.DateTimeField(required=True,widget=forms.DateTimeInput(attrs={'type':'text','class':"form-control flatpickr-input datetime"}))

            # Add Calender selector for Date time fields
            if isinstance(field, TimeField):    
                self.fields[name] = forms.TimeField(required=True,widget=forms.TimeInput(attrs={'type':'time', 'class':"form-control flatpickr-input datetime timepikcr"}))
                 
            # Further customization on Translation fields
            for lang_code in lang_codes:
                # If the field is a translation field
                if name.endswith("_"+lang_code): 
                    original_name = name[:-3] # get the original field name
                    
                    # make the english version the default
                    if lang_code=="en":
                        original = self.fields.get(original_name) # get the original field
                        setattr(field, 'label', str(field.label).replace(" [en]", "")) #Remove the [en] at the end of

                        # If the original field is required, then make the _en version to be required
                        if original and hasattr(original, 'required') and original.required:
                            setattr(field, 'required', True)
                            
                    else: #For other types of languages, just update the label name
                        new_label = str(field.label).replace(f" [{lang_code}]", f" {LANGS[lang_code]}")
                        setattr(field,"label", new_label)
                    
                    # Now add the original field into to_exclude list
                    to_exclude.append(original_name)

            # Finally, Add * for required fields' labels (This has to be at the end)
            if hasattr(field,'required') and field.required:
                label = getattr(field,'label',name)
                setattr(field,'label',label+" *")


        # Exclude original fields
        for name in to_exclude:
            if name in self.fields:
                self.fields.pop(name)
        

    def clean_bid_close_date(self):
        end_date = self.cleaned_data.get('bid_close_date')
        open_date = self.cleaned_data.get('bid_open_date')

        if end_date < open_date:
            raise forms.ValidationError("Bid end date should not exceed bid open date.")
        return end_date
    
    # def clean_bid_open_date(self):
    #     open_date = self.cleaned_data.get('bid_open_date')
    #     if open_date < datetime.datetime.now():
    #         raise forms.ValidationError("Bid open date can't be before today.")
    #     return open_date

def get_form(model:Model, fields="__all__", exclude = None):
    return modelform_factory(model=model, form=TranslatedForm, fields=fields, exclude=exclude ) 
