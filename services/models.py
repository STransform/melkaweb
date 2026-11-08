from django.db import models

from django.conf import settings

class TechnologyService(models.Model):
    """ Model for the detail page of Technology page"""
    is_single = True # Tells if the model should have multiple or single objects
    title = models.CharField(max_length=100, help_text= "Max of 100 Characters.")
    content = models.TextField(help_text= "Make sure that the has a max of 100 words.")
    image = models.ImageField(upload_to='about_images/', blank=False, help_text="Make sure to submit 200 X 300 images.")

    
    class Meta:
        verbose_name = "Technology Service"
        verbose_name_plural = "Technology Service"
    
    
    def __str__(self):
        return f"Technology Page Content"
    

class InfrastructureService(models.Model):
    """ Model for the detail page of Technology page"""
    is_single = True # Tells if the model should have multiple or single objects
    title = models.CharField(max_length=100, help_text= "Max of 100 Characters.")
    content = models.TextField(help_text= "Make sure that the has a max of 100 words.")
    image_one = models.ImageField(upload_to='about_images/', blank=False, help_text="Make sure to submit 200 X 300 images.")

    
    class Meta:
        verbose_name = "Infrastructure"
        verbose_name_plural = "Infrastructure"
    
    
    def __str__(self):
        return f"Infrastructure Page Content"
    
    
class InnovationService(models.Model):
    """ Model for the detail page of Technology page"""
    is_single = True # Tells if the model should have multiple or single objects
    title = models.CharField(max_length=100, help_text= "Max of 100 Characters.")
    content = models.TextField(help_text= "Make sure that the has a max of 100 words.")
    image_one = models.ImageField(upload_to='about_images/', blank=False, help_text="Make sure to submit 200 X 300 images.")

    
    class Meta:
        verbose_name = "Innovation"
        verbose_name_plural = "Innovation"
    
    
    def __str__(self):
        return f"Innovation Page Content"
    
    
