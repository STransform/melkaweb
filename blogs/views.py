from django.shortcuts import render,redirect
from .models import *
from django.shortcuts import render
from django.views import View
from django.contrib import messages
from core.views import paginate
from django.utils.translation import gettext as _

class BlogList(View):
    def get(self, request):
        blogs = Blog.objects.all()
        blogs_list = paginate( blogs, 6, request)
        
        return render(request, 'front/blog.html', {'blogs': blogs_list, 'page_title': 'Blogs','page_subtitle': 'YOU CAN FIND ALL THE RESOURCES IN THIS SECTION',
        'blog_page': True})

class blog_detail(View):
    def get(self, *args, **kwargs):
        blog_id = self.kwargs['blog_id']
        blog = Blog.objects.get(id=blog_id)
        recent_blogs = Blog.objects.all().exclude(id=blog_id).order_by('-pk')[:4]
        return render(self.request, 'front/blog_detail.html', {'blog': blog,'recent_blogs':recent_blogs, 'comments': blog.comments(), 'page_title': 'Blog Detail',  'page_subtitle': '', 
        'blog_page': True})
    
    def post(self, *args, **kwargs):
        blog = Blog.objects.get(id = self.kwargs['blog_id'])
        data = self.request.POST
        BlogComment.objects.create(blog =blog, author = data['author'], email = data['email'], message = data['message'])
        messages.success(self.request, _("Successfully commented! Thank you for your comment. Your comment will be visible once approved by our web managers."))
        return redirect("blog_detail", blog_id= blog.id,)
     
