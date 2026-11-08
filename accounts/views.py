from typing import Any
from django.views import View
from django.utils import timezone
from django.http import HttpRequest
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session 
from django.core.exceptions import PermissionDenied
from django.contrib.auth.hashers import check_password
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponse as HttpResponse
from django.contrib.auth.mixins import PermissionRequiredMixin as DjangoPermissionRequiredMixin

from .forms import *
from .models import UserProfile
from blogs.models import Blog
#from task_manager.models import Task

# user registration page
class Signup(View):
    def get(self,*args, **kwargs):
        return render(self.request, "register.html", {'form':MyUserRegistrationForm()})
    def post(self, *args, **kwargs):
        form =  MyUserRegistrationForm(self.request.POST)
        if form.is_valid():
            form.save()
            messages.success(self.request, "Successfully created user account")
            return redirect("/") 
    
        messages.error(self.request, "Invalid data detected!")
        return render(self.request, "register.html", {'form':form})
    
# log in page
class Login(View):
    @staticmethod
    def _get_user_status(user):
        return getattr(user, "status", "Active")

    @staticmethod
    def _get_user_display_name(user):
        full_name = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
        return full_name or getattr(user, "username", "") or getattr(user, "email", "User")

    def get (self, request):
        user = self.request.user
        if  user.is_authenticated:
            messages.info(self.request, "You are already logged in!")
            if user.is_staff:
                return redirect("admin_dashboard")
            return redirect("/")
        return render (request, 'login.html', )
    
    def post (self, request):
        identifier = (request.POST.get('email') or "").strip()
        password = request.POST.get('password') or ""
        form = AuthenticationForm(request=request, data=request.POST)
        user = authenticate(request, email=identifier, username=identifier, password=password)
        
        # account validation
        if user is not None:
            if not user.is_active:
                messages.warning(request, "Your account is inactive. Please contact an administrator.")
                return render(request, 'login.html', {'form': form})

            if self._get_user_status(user) == 'Active' or user.is_superuser:
                login(request, user)        
                messages.success(request, f'Welcome back {self._get_user_display_name(user)}')
                if user.is_staff:
                    return redirect("admin_dashboard")
                next_url = request.GET.get("next") or request.POST.get("next")
                if next_url:
                    return redirect(next_url)
                return redirect("/")
            elif self._get_user_status(user) == 'Account Activation':
                messages.warning(request, f"Your account is being verified by our staff. Account status on {self._get_user_status(user)}")    
            else:
                messages.warning(request, f"You can't login because your account status is on {self._get_user_status(user)}.")    
                
            return redirect("/")
        

        else:
            messages.warning(request, 'Email/username or password is wrong!',)
            return render(request, 'login.html', {'form':form})
 
    
class Logout(LoginRequiredMixin,View):
    def get(self, request):
        logout(self.request)
        messages.success(request, 'Successfully logged out.')
        return redirect ( '/')
    

class Profile(LoginRequiredMixin,View):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        user = UserProfile.objects.get(id=self.kwargs['id'])
        if self.request.user != user and not self.request.user.has_perm('accounts.change_userprofile'):
            raise PermissionDenied("You can't access this page")
        
        return super().dispatch(request, *args, **kwargs)
    
    # render user profile page
    def get(self, request, id):
        
        user = UserProfile.objects.get(id=id)
        form = EditProfileForm(instance=user)
       # tasks = Task.objects.filter(assigned_to=user)[:5]
        blogs = Blog.objects.all()[:3]
        password_form = None
        if self.request.user == user:
            password_form = ChangePasswordForm()
            title = 'My'
        else:
            password_form = ResetPasswordForm()
            title = 'User'
        
        user_sessions = []
        # If user is on my profile page show active sessions 
        if title == 'My':
            all_active_sessions = Session.objects.filter(expire_date__gte=timezone.now()).order_by('expire_date').reverse()
            for session in all_active_sessions:
                # If the user id of the this session is the same as the logged in user, add it to user_sessions list 
                if session.get_decoded().get('_auth_user_id', None) == str(user.id):
                    user_sessions.append(session)
                
        return render(request, 'staff/accounts/profile.html', {'user_obj': user,'user_sessions':user_sessions,'current_session_key':self.request.session.session_key, 'blogs':blogs, 'form':form,'password_form':password_form, 'title':title })
    
    # update user profile data
    def post(self,request, id):
        user = UserProfile.objects.get(id=id)
        form = EditProfileForm(instance=user, data=self.request.POST, files=self.request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            form.save_m2m()
            messages.warning(self.request,'Profile updated successfully')
            return redirect( 'profile', id=id)
        else:
            messages.warning(self.request,'unable to update profile')
            
            return render(request, 'staff/accounts/profile.html', {'user_obj':user})

# Change current user's password view
class ChangePassword(LoginRequiredMixin,View):
    def post(self, request, id):
        user = UserProfile.objects.get(id=id)
        password_form = ChangePasswordForm(data=self.request.POST)
        if password_form.is_valid():
            if check_password(password_form.data['current_password'],user.password): 
                new_pw = password_form.data['new_password']
                user.set_password(new_pw)
                user.save()
                messages.success(self.request,'Successfully changed your password! Please login with your new credentials!')
                return redirect("login")
            
            else:
                messages.warning(self.request,'Current password is not correct!')
                return redirect ('profile', id=id)
        else:
            messages.warning(self.request,f'{password_form.errors.as_text()}')
            return redirect ('profile', id=id)
        

# users list
class UsersList(LoginRequiredMixin,DjangoPermissionRequiredMixin,View):
    permission_required =['accounts.view_userprofile']
    def get (self, *args, **kwargs):
        model = UserProfile
        if not model:
            messages.error(self.request, "Page not found!")
            return redirect("admin_dashboard")
        
        model, 
        objs = model.objects.all()
        list_fields = getattr(model, 'list_fields',[])
        return render(self.request, "staff/accounts/list_user.html",  {'objs':objs,'fields':list_fields}) 


# create account for new members 
class AddUser(LoginRequiredMixin,DjangoPermissionRequiredMixin,View):
    permission_required=['accounts.add_userprofile']
    def get(self,*args, **kwargs):
        return render(self.request, "staff/accounts/add_user.html", {'form':MyUserRegistrationForm()})
    def post(self, *args, **kwargs):
        form =  MyUserRegistrationForm(self.request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(self.request, "Successfully created user account")
            return redirect("users_list") 
    
        messages.error(self.request, "Invalid data detected!")
        return render(self.request, "staff/accounts/add_user.html", {'form':form})
    

# Reset another user's password
class ResetPassword(LoginRequiredMixin,DjangoPermissionRequiredMixin,View):
    permission_required =['accounts.change_userprofile']
    def post(self, request, id):
        user = UserProfile.objects.get(id=id)
        password_form = ResetPasswordForm(data=self.request.POST)
        
        if password_form.is_valid():
            new_pw = password_form.data['new_password']
            user.set_password(new_pw)
            user.save()
            messages.success(self.request,'Successfully changed user password!')
            return redirect ('profile', id=id)
            
        else:
            messages.warning(self.request,f'{password_form.errors.as_text()}')
            return render(request, 'staff/accounts/profile.html',{'user_obj':user, 'password_form':password_form})
    


class DeleteUser(LoginRequiredMixin,DjangoPermissionRequiredMixin, View):
    permission_required =['accounts.delete_userprofile']
    def get (self, request, id):
        try:
            user = UserProfile.objects.get(id=id)
            user.delete()
            messages.success(self.request,"Successfully deleted a user!")
        except Exception as e:
            messages.warning(self.request, f"An Exception occurred while trying to delete this user. {e}")
            return redirect ('users_list')
         
