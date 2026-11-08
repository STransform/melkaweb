from django.db import models
from django.conf import settings

class About(models.Model):
    """ Model for the detail page of about us page"""
    #is_single = True # Tells if the model should have multiple or single objects
    title = models.CharField(max_length=100, help_text= "Max of 100 Characters.")
    content = models.TextField(help_text= "Make sure that the has a max of 100 words.")
    mission = models.TextField(help_text= "Make sure that the has a max of 100 words.")
    vision = models.TextField(help_text= "Make sure that the has a max of 100 words.")
    values = models.TextField(help_text= "Make sure that the has a max of 100 words.")
    image_one = models.ImageField(upload_to='about_images/', blank=False, help_text="Make sure to submit 200 X 300 images.")
    image_two = models.ImageField(upload_to='about_images/', blank=False, help_text="Make sure to submit 200 X 300 images.")
    image_three = models.ImageField(upload_to='about_images/', blank=False, help_text="Make sure to submit 200 X 300 images.")
    
    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f"{self.title} | {self.content}"

    def get_list_fields():
        return ['title', 'content',]
    list_fields = get_list_fields()
        
class CompanyValues(models.Model):
    """ Model for the detail page of about us page"""
    # is_single = True # Tells if the model should have multiple or single objects
    title = models.CharField(max_length=100, help_text= "Max of 100 Characters.")
    content = models.TextField(help_text= "Make sure that  has a max of 100 words.")
    
    class Meta:
        verbose_name = "Core Values"
        verbose_name_plural = "Core Values"
    
    
    def __str__(self):
        return f"Core Values "
class OurPartners(models.Model):
    # Model for the our partner page
    image = models.ImageField(upload_to='bureau_structure_images/', help_text="Make sure to submit an image proportional to the content")

    class Meta:
        verbose_name = "Our Partners "
        verbose_name_plural = "Our Partners"
    
    
    def __str__(self):
        return f"Our Partners"
    

class VisionMission(models.Model):
    """ Model for the detail page of about us page"""
    # is_single = True # Tells if the model should have multiple or single objects
    title = models.CharField(max_length=100, help_text= "Max of 100 Characters.")
    content = models.TextField(help_text= "Make sure that  has a max of 100 words.")
    
    class Meta:
        verbose_name = "Vision Mission"
        verbose_name_plural = "Vision Mission"
    
    
    def __str__(self):
        return f"Vision Mission "

class Vision(models.Model):
    """ Model for the detail page of about us page"""
    is_single = True # Tells if the model should have multiple or single objects
    title = models.CharField(max_length=100, help_text= "Max of 100 Characters.")
    content = models.TextField(help_text= "Make sure that  has a max of 100 words.")
    
    class Meta:
        verbose_name = "Vision "
        verbose_name_plural = "Vision "
    
    
    def __str__(self):
        return f"Vision  "
    
class AboutOtechFooter(models.Model):
    """ Model for the detail page of about us page"""
    is_single = True # Tells if the model should have multiple or single objects
    title = models.CharField(max_length=100, help_text= "Max of 100 Characters.")
    content = models.TextField(help_text= "Make sure that  has a max of 100 words.")
    
    class Meta:
        verbose_name = "About Us "
        verbose_name_plural = "About Us "
    
    
    def __str__(self):
        return f"About Us  "

class OtechExcellence(models.Model):
    """ Model for the detail page of about us page"""
    is_single = True # Tells if the model should have multiple or single objects,Director message should not be many pages...it should be one page only

    title1 = models.CharField(max_length=255,help_text="Make sure to submit a max of 255 characters.",default="title")
    content1 = models.TextField(default="default")
    title2 = models.CharField(max_length=255,help_text="Make sure to submit a max of 255 characters.",default="title")
    content2 = models.TextField(default="default")
    title3 = models.CharField(max_length=255,help_text="Make sure to submit a max of 255 characters.",default="title")
    content3 = models.TextField(default="default")
    image = models.ImageField(upload_to='slider_images/',help_text="Make sure to submit an image proportional with the height of the content.", default='default_image.png')
    
    def __str__(self):
        return self.title1

class WhatPeopleSays(models.Model):
    """ Model for the detail page of about us page"""
    #is_single = True # Tells if the model should have multiple or single objects,Director message should not be many pages...it should be one page only

    
    content = models.TextField(help_text= "Make sure that  has a max of 100 words.")
    image = models.ImageField(upload_to='slider_images/',help_text="Make sure to submit an image proportional with the height of the content.")
    full_name = models.CharField(max_length=255,help_text="Make sure to submit a max of 255 characters.")
    position = models.CharField(max_length=255,help_text="Make sure to submit a max of 255 characters.")
    class Meta:
        verbose_name = "What People Says "
        verbose_name_plural = "What People Says "
    
    
    def __str__(self):
        return f"What People Says "
       
class TeamMember(models.Model):
    # Model for the section inside the about us, which lists Management experts
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, help_text="Working position of the individual.")
    image = models.ImageField(upload_to='team_members/', help_text="Make sure to submit 300 X 400 images.")
    social_facebook = models.URLField(blank=True)
    social_twitter = models.URLField(blank=True)
    social_google_plus = models.URLField(blank=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f"{self.name} | {self.role}"

    def get_list_fields():
        return ['name', 'role',]
    list_fields = get_list_fields()
    
    
class BureauStructure(models.Model):
    is_single = True # Tells if the model should have multiple or single objects
    # Model for the Bureau structure page
    title = models.CharField(max_length=100, help_text="Make sure to submit a max of 50 words.")
    content = models.TextField(help_text="Make sure to submit a content that aligns with the height of the image")
    image = models.ImageField(upload_to='bureau_structure_images/', help_text="Make sure to submit an image proportional to the content")
    management_board_title = models.CharField(max_length=100,help_text="Make sure to submit a max of 100 characters.")
    management_board_content = models.TextField(help_text="Make sure to submit a content that aligns with the height of the image")
    execution_team_title = models.CharField(max_length=100,help_text="Make sure to submit a max of 100 characters.")
    execution_team_content = models.TextField(help_text="Make sure to submit a content that aligns with the height of the image")
    execution_team_image = models.ImageField(upload_to='bureau_structure_images/',
                                             help_text="Make sure to submit an image proportional to the execution team content")

    def __str__(self):
        return f"Bureau Structure Content "
    

class Service(models.Model):
    # Model for the our service page
    title = models.CharField(max_length=100, help_text="Make sure to submit a max of 100 characters.")
    content = models.TextField(help_text="Would be great if you can summarize the content with a max of 500 characters.")
    created_date = models.DateTimeField(auto_now_add = True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True) 

    def __str__(self):
        return self.title

    def get_list_fields():
        return ['title', 'created_by', 'created_date']
    
    list_fields = get_list_fields()
    excluded_fields = ['created_by']


class Technology(models.Model):
    # Model for the our service page
    title = models.CharField(max_length=100, help_text="Make sure to submit a max of 100 characters.")
    content = models.TextField(help_text="Would be great if you can summarize the content with a max of 500 characters.")
    image = models.ImageField(upload_to='bureau_structure_images/', help_text="Make sure to submit an image proportional to the content")

    class Meta:
        verbose_name = "Technology"
        verbose_name_plural = "Technology"
    
    
    def __str__(self):
        return f"Technology Page Content"

class Infrastructure(models.Model):
    # Model for the our service page
    infr_title = models.CharField(max_length=100, help_text="Make sure to submit a max of 100 characters.")
    infr_content = models.TextField(help_text="Would be great if you can summarize the content with a max of 500 characters.")
    infr_image = models.ImageField(upload_to='bureau_structure_images/', help_text="Make sure to submit an image proportional to the content")

    class Meta:
        verbose_name = "Infrastructure"
        verbose_name_plural = "Infrastructure"
    
    
    def __str__(self):
        return f"Infrastructure Page Content"
    
class Innovation(models.Model):
    # Model for the our service page
    invn_title = models.CharField(max_length=100, help_text="Make sure to submit a max of 100 characters.")
    invn_content = models.TextField(help_text="Would be great if you can summarize the content with a max of 500 characters.")
    invn_image = models.ImageField(upload_to='bureau_structure_images/', help_text="Make sure to submit an image proportional to the content")

    class Meta:
        verbose_name = "Innovation"
        verbose_name_plural = "Innovation"
    
    
    def __str__(self):
        return f"Innovation Page Content"

class ElevatingSkills(models.Model):
    is_single = True
    title = models.CharField(max_length =255,help_text="Make sure to submit a max of 255 characters.")
    # video = models.FileField(upload_to="Gallery/Videos", blank=True, null=True)
    content = models.TextField(help_text="Would be great if you can summarize the content with a max of 500 characters.")
    link = models.CharField(max_length=10000, blank=True,default="", help_text="Please submit the embed link, not the url link.")
    
    
    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return self.title
    
    
    def get_list_fields():
        return ['title']
    
    list_fields = get_list_fields()