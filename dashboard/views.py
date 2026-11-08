from core.presentation import render
from django.views import View
from django.apps import apps
from django.conf import settings
from django.db import ProgrammingError
from django.db.models.base import ModelBase
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import Group

from blogs.models import *
from core.forms import get_form
from core.models import ContactUs
from dashboard.models import Event 
from news.models import NewsArticle
from task_manager.models import Task 
from documents.models import Document
from suppliers.models import Supplier, ArchivedSupplier
from vacancies.models import Job, Application
from dashboard.models import GalleryImage, GalleryVideo
from django.contrib.admin.models import LogEntry
from django.contrib.auth.mixins import AccessMixin, PermissionRequiredMixin as DjangoPermissionRequiredMixin


def get_model(name):
    if name=='Group': return (Group,"django.contrib.auth")
    for app_label in settings.CUSTOM_INSTALLED_APPS:
        try:
            model = apps.get_model(app_label=app_label, model_name=name) 
            return (model, app_label)
        except LookupError:# no such model in this application
            pass
    return (None, None)   

def get_conf(request, kwargs):
    model,app_label = get_model(kwargs['model_name'])
    if model: 
        model_name:str = model._meta.verbose_name or kwargs['model_name'].capitalize()
        excluded_fields = getattr(model, 'excluded_fields') if hasattr(model, 'excluded_fields') else None
        form =  get_form(model, exclude = excluded_fields)
        is_single = getattr(model,'is_single',False)
        return {"model":model, "form":form, "model_name": model_name,"app_label":app_label,"single": is_single}
    return None


class PermissionRequiredMixin(AccessMixin):
    """Verify that the current user has all specified permissions."""
    permission_required = "view"

    def dispatch(self, request, *args, **kwargs):
        self.config = get_conf(self.request, self.kwargs)
        if not self.config:
            messages.error(self.request, "Page not found!")
            return redirect("admin_dashboard")
        
        app_lebel = self.config["app_label"]
        real_model_name = self.kwargs['model_name'].lower()
        perm = f"{app_lebel}.{self.permission_required}_{real_model_name}"
        
        if not self.request.user.has_perm(perm):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

# render staff dashboard page
class Dashboard(LoginRequiredMixin, View ):
    def get(self, request):
        task_data = {
            'all': 0,
            'done': 0,
            'progress': 0,
            'pending': 0,
        }
        try:
            tasks = Task.objects.all()
            task_data = {
                'all': tasks.count(),
                'done': tasks.filter(status='Completed').count(),
                'progress': tasks.filter(status='Inprogress').count(),
                'pending': tasks.filter(status='Pending').count()
            }
        except ProgrammingError:
            # Allow the dashboard to load before optional task manager tables are migrated.
            pass
        return render(request, 'staff/admin_home.html', 
                      { 'index':True,
                        'tasks':task_data, 
                        'jobs':Job.objects.count(), 
                        'applications':Application.objects.count(), 
                        'events':Event.objects.all(),
                        'galleries':GalleryImage.objects.count(), 
                        'videos':GalleryVideo.objects.count(),
                        'docs':Document.objects.count(),
                        'news':NewsArticle.objects.count(),
                        'blogs':Blog.objects.count(),
                        'contactus': ContactUs.objects.all()[:5],
                        'blocked_supplier':Supplier.objects.all()[:5]
                       }
                    )
    
# creates an object for requested model
class CreateView(LoginRequiredMixin,PermissionRequiredMixin, View):
    permission_required = "add"
    def get(self, *args, **kwargs):
        config = self.config
        model, model_name  = config["model"], config["model_name"] 
        form = config["form"] 
        if config["single"] and model.objects.first(): # if model object has to be generated only once
            return redirect("change_view", model_name = kwargs['model_name'], pk=model.objects.first().id)
        
        
        return render(self.request, 'staff/create_page.html', { 'add':True,  'form':form, 'is_single':config["single"], 
                                                                'model_code':self.kwargs['model_name'],
                                                                'model_name':model_name.capitalize(),})
    
    def post(self, *args, **kwargs):
        config = self.config
        model = config["model"]
        form = config["form"](self.request.POST, self.request.FILES)
        if form.is_valid():
            obj  = form.save(commit = False)
            if hasattr(model, 'created_by'):
                setattr(obj, 'created_by', self.request.user)
            obj.save()
            messages.success(self.request, f"Successfully created !")
            if config['single']:
                return redirect("admin_dashboard" )
            return redirect("list_view", model_name = self.kwargs['model_name'])

        model_name = config["model_name"]
        return render(self.request, 'staff/create_page.html', { 'add':True,  'form':form, 'is_single':config["single"], 
                                                                'model_code':self.kwargs['model_name'],
                                                                'model_name':model_name.capitalize(),})
        
# Updates an object for requested model
class ChangeView(LoginRequiredMixin,PermissionRequiredMixin, View):
    permission_required = "change"
    def get(self, *args, **kwargs):
        config = self.config
        model, model_name = config["model"], config["model_name"]
        
        # if model is single, just bring the first object
        if config['single']:
            obj = model.objects.first()
            # if there is no object created for this single item page, redirect to create view
            if not obj: 
                return redirect("create_view", model_name = model_name)
        
        # If model can have multiple objects, fetch the object with the pk
        else: 
            obj = model.objects.get(id = self.kwargs['pk'])
        form = config["form"](instance = obj)
        
        # list objects derived from other models (job & application, blog & comment)
        child_obj, child_obj_fields  = None, [] 

        if model == Job:
            child_obj = obj.application_set.all()
        elif model == Blog:
            child_obj = obj.comment_set.all()
        
        # Get list fields of the child object
        child_obj_fields = getattr(child_obj.model, 'list_fields',[]) if child_obj else []

        return render(self.request, 'staff/create_page.html', { 'add':False,  'form':form, 'is_single':config['single'], 'current_obj':obj,
                                                                'model_name':model_name.capitalize(), 'model_code':self.kwargs['model_name'], 'pk':self.kwargs['pk'],
                                                                'child_obj':child_obj, 'child_obj_fields':child_obj_fields})
    
    def post(self, *args, **kwargs):
        config = self.config
        model, model_name = config["model"], config["model_name"]
        obj = model.objects.get(id = self.kwargs['pk'])
        form = config["form"](self.request.POST,self.request.FILES,instance = obj)
        if form.is_valid():
            form.save()
            messages.success(self.request, f"Successfully updated {model_name}!")
            if config['single']:
                return redirect("admin_dashboard" )
            return redirect("list_view", model_name = self.kwargs['model_name'])
        
        messages.warning(self.request, "Invalid data detected. Please review your inputs and try again.")
        return render(self.request, 'staff/create_page.html', { 'add':False,  'form':form, 'is_single':config['single'], 
                                                                'model_name':model_name.capitalize(),})
    
# lists of objects for requested model
class ListView(LoginRequiredMixin,PermissionRequiredMixin, View):
    permission_required = "view"
    def get(self, *args, **kwargs):
        config = self.config
        model, formal_name = config["model"], config["model_name"]
        # if model is single, just bring the first object
        if config['single']:
            return redirect("create_view", model_name = self.kwargs['model_name'])
        
        objs = model.objects.all()
        list_fields = getattr(model, 'list_fields',[])
        
        return render (self.request, "staff/list_page.html", 
                      {'model_name':formal_name, 'model_code':self.kwargs['model_name'], 'single':config['single'],
                       'objs':objs,'fields':list_fields}
                    ) 

# deletes an object for requested model
class DeleteView(LoginRequiredMixin,PermissionRequiredMixin, View):
    permission_required = "delete"
    def get(self, *args, **kwargs):
        config = self.config
        model, model_name = config["model"], config["model_name"]
        
        # if model is single, just bring the first object
        if config['single']:
            print("You can't delete this item, you can only update it's values!")
            return redirect("admin_dashboard")
    
        obj = model.objects.get(id=self.kwargs['pk'])

        if model == Supplier:
            ArchivedSupplier.objects.create(
                tin=obj.tin,
                company_name=obj.company_name,
                legal_form=obj.legal_form,
                nationality=obj.nationality,
                area_of_business=obj.area_of_business,
                sector=obj.sector,
                description=obj.description,
                document=obj.document,
                created_by=obj.created_by,
                created_date=obj.created_date,
            ).save()

        obj.delete()
        messages.success(self.request, f"Successfully deleted {model_name}")
        return redirect("list_view",model_name=self.kwargs['model_name'])
        

class ApproveComment(LoginRequiredMixin,DjangoPermissionRequiredMixin, View):
    permission_required = ("blogs.change_blog")
    def get(self, *args, **kwargs):
        comment = BlogComment.objects.get(id=self.kwargs['pk'])
        comment.approved= True if not comment.approved else False
        comment.save()
        msg = f"Successfully approved comment to be seen" if comment.approved else f"Successfully hidden comment from being seen"
        messages.success(self.request, msg)
        return redirect("change_view", model_name='Blog', pk=comment.blog.id)
        
# show archived blocked suppliers detail
class SupplierDetail(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        suppliers = ArchivedSupplier.objects.filter(tin=self.kwargs['tin'])
        return render (self.request, "staff/supplier_detail.html", {'suppliers':suppliers})
    
    
