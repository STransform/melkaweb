"""Public, explicitly allowlisted content API for the Next.js frontend.

Staff operations and authentication remain owned by Django. No generic model or
user serializer is exposed here, and writes retain Django's CSRF protection.
"""
import logging

from django import forms
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from about_us import models as about
from blogs.models import Blog, BlogComment
from core.models import ContactUs, Pages, Settings
from dashboard import models as dashboard
from documents.models import Document
from news.models import NewsArticle
from visit_counter.models import UserVisit
from vacancies.models import Job

logger = logging.getLogger(__name__)

# Model, fields, title. Never serialize foreign-key users or private settings.
RESOURCES = {
    'news': (NewsArticle, 'title content featured_image minutes_read created_at', 'News'),
    'blogs': (Blog, 'title content images created_date', 'Blogs'),
    'documents': (Document, 'title description category file upload_date', 'Documents'),
    'gallery-images': (dashboard.GalleryImage, 'title image', 'Gallery images'),
    'gallery-videos': (dashboard.GalleryVideo, 'title link', 'Gallery videos'),
    'events': (dashboard.Event, 'title image location description date time', 'Events'),
    'bids': (dashboard.Bid, 'title description bid_open_date bid_close_date bid_document', 'Bids'),
    'about': (about.About, 'title content mission vision values image_one image_two image_three', 'About us'),
    'services': (about.Service, 'title content', 'Services'),
    'technology': (about.Technology, 'title content image', 'Technology'),
    'infrastructure': (about.Infrastructure, 'infr_title infr_content infr_image', 'Infrastructure'),
    'innovation': (about.Innovation, 'invn_title invn_content invn_image', 'Innovation'),
    'companyvalues': (about.CompanyValues, 'title content', 'Our values'),
    'visionmission': (about.VisionMission, 'title content', 'Vision and mission'),
    'vision': (about.Vision, 'title content', 'Vision'),
    'otech_excellence': (about.OtechExcellence, 'title1 content1 title2 content2 title3 content3 image', 'Excellence'),
    'people_saying': (about.WhatPeopleSays, 'content image full_name position', 'Testimonials'),
    'about_footer': (about.AboutOtechFooter, 'title content', 'Our story'),
    'elevating_skills': (about.ElevatingSkills, 'title content link', 'Elevating skills'),
    'our_partners': (about.OurPartners, 'image', 'Our partners'),
    'bureau_structure': (about.BureauStructure, 'title content image management_board_title management_board_content execution_team_title execution_team_content execution_team_image', 'Our structure'),
}


def serialize(obj, fields):
    if obj is None:
        return None
    data = {'id': obj.pk}
    for name in fields.split():
        value = getattr(obj, name, '')
        if isinstance(value, models.fields.files.FieldFile):
            value = value.url if value else None
        data[name] = value
    if isinstance(obj, (Blog, NewsArticle)):
        category = obj.category()
        data['category'] = str(category) if category else ''
        data['url'] = reverse('blog_detail', kwargs={'blog_id': obj.pk}) if isinstance(obj, Blog) else reverse('news_detail', kwargs={'news_id': obj.pk})
        data['author'] = str(obj.created_by)
    return data


def collection(name, limit=None):
    model, fields, _title = RESOURCES[name]
    queryset = model.objects.all().order_by('-pk')
    if limit is not None:
        queryset = queryset[:limit]
    return [serialize(obj, fields) for obj in queryset]


def site_data(request):
    settings_obj = Settings.objects.first()
    pages = Pages.objects.first()
    return {
        'settings': serialize(settings_obj, 'title logo email address working_hours facebook youtube instagram twitter linkedin map_link'),
        'pages': serialize(pages, 'about structure services documents blocked_suppliers bid events vacancy news blogs gallery contact_us'),
        'contacts': [serialize(obj, 'address phone email website') for obj in dashboard.Contact.objects.all()],
        'quick_links': [serialize(obj, 'title url') for obj in dashboard.QuickLink.objects.all()],
        'user': {'authenticated': request.user.is_authenticated, 'staff': request.user.is_staff,
                 'name': request.user.first_name if request.user.is_authenticated else ''},
        'labels': {text: _(text) for text in ['Home', 'About us', 'Services', 'News', 'Blogs', 'Documents', 'Events', 'Gallery images', 'Gallery videos', 'Bids', 'Contact us', 'Search', 'Sign in', 'Sign out', 'Dashboard', 'Careers', 'Suppliers', 'Read more', 'Previous', 'Next', 'No results found.', 'Send message', 'Your name', 'Email', 'Phone', 'Subject', 'Message']},
    }


@never_cache
@require_GET
def site(request):
    return JsonResponse(site_data(request))


@never_cache
@require_GET
def home(request):
    data = {key: collection(key, 9) for key in ['blogs', 'news', 'documents', 'gallery-images', 'companyvalues', 'visionmission', 'vision', 'otech_excellence', 'people_saying', 'about_footer', 'elevating_skills', 'our_partners', 'services']}
    data['featured_works'] = [serialize(obj, 'title description background_image') for obj in dashboard.FeaturedWork.objects.all()]
    data['director'] = serialize(dashboard.DirectorateMessage.objects.first(), 'title content image')
    data['faqs'] = [serialize(obj, 'question answer') for obj in dashboard.FAQ.objects.all()]
    data['visitors'] = UserVisit.objects.count()
    data['hero_copy'] = {
        'title': _('Transformation — for a better tomorrow.'),
        'description': _('Our mission is to create intelligent, inclusive, and transformative software solutions that redefine how people and organizations thrive.'),
        'badge': _('Build. Automate. Elevate'),
    }
    data['service_highlights'] = [
        {'id': 1, 'title': _('Software Solutions'), 'content': _('We build custom software solutions from the ground up — combining innovation, functionality, and scalability to empower organizations with modern digital experiences.'), 'url': reverse('technology')},
        {'id': 2, 'title': _('Network & Cybersecurity'), 'content': _('We design and deploy secure, high-performance network infrastructures and protect your systems with advanced cybersecurity solutions.'), 'url': reverse('infrastructure')},
        {'id': 3, 'title': _('Innovation & Quantum Solutions'), 'content': _('Strategic consulting and innovative solutions to keep your business ahead of the competition with forward-thinking strategies.'), 'url': reverse('innovation')},
    ]
    return JsonResponse(data)


@never_cache
@require_GET
def resource(request, name, pk=None):
    if name not in RESOURCES:
        return JsonResponse({'error': 'Not found'}, status=404)
    model, fields, title = RESOURCES[name]
    if pk is not None:
        obj = get_object_or_404(model, pk=pk)
        data = serialize(obj, fields)
        if name == 'blogs':
            data['comments'] = [serialize(comment, 'author message created_at') for comment in obj.comments()]
        return JsonResponse({'title': _(title), 'item': data})
    queryset = model.objects.all().order_by('-pk')
    term = request.GET.get('q', '').strip()
    if term:
        searchable = [field for field in fields.split() if 'title' in field or field in ('description', 'content')]
        query = Q()
        for field in searchable:
            query |= Q(**{f'{field}__icontains': term})
        if searchable:
            queryset = queryset.filter(query)
    if request.GET.get('category') and name == 'documents':
        queryset = queryset.filter(category=request.GET['category'])
    page = Paginator(queryset, 12).get_page(request.GET.get('page'))
    data = {'title': _(title), 'items': [serialize(obj, fields) for obj in page],
            'page': page.number, 'pages': page.paginator.num_pages, 'total': page.paginator.count}
    if name == 'about':
        data['team'] = [serialize(obj, 'name role image social_facebook social_twitter social_google_plus') for obj in about.TeamMember.objects.all()]
    return JsonResponse(data)


@never_cache
@require_GET
def search(request):
    term = request.GET.get('searched_item', '').strip()
    groups = {}
    if term:
        for name in ['news', 'blogs', 'documents', 'events', 'gallery-images']:
            model, fields, title = RESOURCES[name]
            filters = Q(title__icontains=term)
            if name in ['news', 'blogs']:
                category = 'news_category' if name == 'news' else 'blog_category'
                filters |= Q(**{f'{category}__name__icontains': term}) | Q(created_by__first_name__icontains=term)
            elif name == 'documents':
                filters |= Q(category__icontains=term)
            elif name == 'gallery-images':
                filters |= Q(gallery_category__name__icontains=term)
            elif name == 'events':
                filters |= Q(location__icontains=term)
            queryset = model.objects.filter(filters).order_by('-pk')[:30]
            groups[name] = {'title': _(title), 'items': [serialize(obj, fields) for obj in queryset]}
        jobs = Job.objects.filter(Q(job_title__icontains=term) | Q(job_type__icontains=term) | Q(Status__icontains=term), Status='Active')[:30]
        groups['jobs'] = {'title': _('Careers'), 'items': [
            {'id': job.pk, 'title': job.job_title, 'description': job.job_description,
             'url': reverse('jobs_apply', kwargs={'pk': job.pk})} for job in jobs
        ]}
    return JsonResponse({'term': term, 'groups': groups})


@never_cache
@ensure_csrf_cookie
@require_GET
def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['full_name', 'email', 'phone', 'subject', 'message']


class CommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['author', 'email', 'message']


@never_cache
@require_POST
def contact(request):
    form = ContactForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    obj = form.save()
    settings_obj = Settings.objects.first()
    recipient = settings_obj.email_for_contact_us if settings_obj else ''
    if recipient:
        try:
            EmailMultiAlternatives(
                f'Visitor message : {obj.subject}',
                f'{obj.full_name} ({obj.email}, {obj.phone})\n\n{obj.message}',
                to=[recipient], reply_to=[obj.email],
            ).send()
        except Exception:
            # A saved message must not appear lost when SMTP is unavailable.
            logger.exception('Contact message %s saved; email notification failed', obj.pk)
    return JsonResponse({'message': _("Successfully sent your feed back to our staff. We'll get back to you soon.")}, status=201)


@never_cache
@require_POST
def comment(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    form = CommentForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    obj = form.save(commit=False)
    obj.blog = blog
    obj.approved = False
    obj.save()
    return JsonResponse({'message': _('Your comment will be visible once approved by our web managers.')}, status=201)


urlpatterns = [
    path('site/', site), path('home/', home), path('search/', search),
    path('csrf/', csrf), path('contact/', contact), path('blogs/<int:pk>/comments/', comment),
    path('content/<str:name>/', resource), path('content/<str:name>/<int:pk>/', resource),
]
