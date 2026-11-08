
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from core.views import index, search, EventListPage, GalleryImagePage, GalleryVideoPage, Contact, BidPage
from django.views.i18n import JavaScriptCatalog
from django.utils.translation import gettext_lazy as _
from django.conf.urls.i18n import i18n_patterns
from about_us.urls import ServicesPage,TechnologyPage

admin.site.site_header = 'Super Administrator'

urlpatterns = [
    path('internalAdmin/', admin.site.urls),
    path('', index, name="index"),#for homage page

    # Include your app-specific URLs here
    path('news/', include('news.urls')),
    path('blogs/', include('blogs.urls')),
    path('accounts/', include('accounts.urls')),
    path('about-us/', include('about_us.urls')),
    path('suppliers/', include('suppliers.urls')),
    path('vacancies/', include('vacancies.urls')),
    path('documents/', include('documents.urls')),  
    path('dashboard/', include('dashboard.urls')), # URLs for internal dashboards
    path('taskmanager/', include('task_manager.urls')),

    # direct urls
    path('search/', search, name='search'), #header search functionality
    path("contact-us/",Contact.as_view(), name="contact_us"),
    path('events/', EventListPage.as_view(), name='events_list'),
    path('gallery-images/', GalleryImagePage.as_view(), name='gallery_images'),
    path('gallery-videos/', GalleryVideoPage.as_view(), name='gallery_videos'),
    path('bids/', BidPage.as_view(), name='bid'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('i18n/', include('django.conf.urls.i18n')),
    
    # error urls
    path('403', TemplateView.as_view(template_name="403.html"), name="403"),
    path('404', TemplateView.as_view(template_name="404.html"), name="404"),
    path('500', TemplateView.as_view(template_name="500.html"), name="500"),
    
    path('filer/', include('filer.urls')),
    path('', include('cms.urls')),
    
    

]

urlpatterns = [
    *i18n_patterns(*urlpatterns, prefix_default_language=False),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

