"""Public tutorial data and session-deduplicated engagement."""
import hashlib
import secrets
from django import forms
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import io
from .models import Blog, BlogCategory, BlogComment, BlogLike, BlogVisit

def published():
    return Blog.objects.filter(published_status='Published').select_related('created_by', 'blog_category').order_by('-published_at', '-pk')

def article_data(blog, request, include_body=True):
    author = f'{blog.created_by.first_name} {blog.created_by.last_name}'.strip() or 'MelkaTech'
    return {
        'id': blog.pk, 'title': blog.title, 'summary': blog.summary, 'content': blog.content if include_body else '', 'format': blog.content_format,
        'url': blog.get_absolute_url(), 'canonical': request.build_absolute_uri(blog.get_absolute_url()),
        'image': blog.images.url if blog.images else '', 'category': str(blog.blog_category or ''),
        'tags': [tag.strip() for tag in blog.tags.split(',') if tag.strip()], 'difficulty': blog.difficulty,
        'prerequisites': blog.prerequisites, 'author': author, 'author_bio': blog.author_bio, 'minutes': blog.reading_minutes,
        'published': (blog.published_at or blog.created_date).isoformat(), 'updated': blog.updated_at.isoformat(),
        'series': blog.series, 'description': blog.seo_description or blog.summary or blog.title,
        'likes': blog.likes.count(), 'views': blog.visits.count(),
    }

def library_data(request):
    rows = published()
    q, category, difficulty = (request.GET.get(key, '').strip()[:200] for key in ['q', 'category', 'difficulty'])
    if q:
        rows = rows.filter(Q(title__icontains=q) | Q(summary__icontains=q) | Q(tags__icontains=q) | Q(content__icontains=q))
    if category:
        rows = rows.filter(blog_category__name=category)
    if difficulty:
        rows = rows.filter(difficulty=difficulty)
    page = Paginator(rows, 9).get_page(request.GET.get('page'))
    return {'items': [article_data(row, request, False) for row in page], 'page': page.number,
            'pages': page.paginator.num_pages, 'total': page.paginator.count,
            'categories': list(BlogCategory.objects.filter(blog__published_status='Published').distinct().values_list('name', flat=True)),
            'q': q, 'category': category, 'difficulty': difficulty, 'canonical': request.build_absolute_uri('/tutorials/')}

def visitor(request):
    if not request.session.get('tutorial_visitor'):
        request.session['tutorial_visitor'] = secrets.token_hex(24)
    return hashlib.sha256(request.session['tutorial_visitor'].encode()).hexdigest()

def rate_allowed(request, action, limit=20):
    key = 'tutorial-rate:' + hashlib.sha256(f'{visitor(request)}:{action}'.encode()).hexdigest()
    if cache.add(key, 1, 60):
        return True
    try:
        return cache.incr(key) <= limit
    except ValueError:
        return False

class TutorialCommentForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)
    class Meta:
        model = BlogComment
        fields = ['author', 'email', 'message']
    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if not message or len(message) > 10000:
            raise forms.ValidationError('Please enter a comment of 1–10,000 characters.')
        return message

@never_cache
@require_POST
def engagement(request, pk, action):
    blog = get_object_or_404(published(), pk=pk)
    if not rate_allowed(request, action, 30):
        return JsonResponse({'detail': 'Please wait a minute before trying again.'}, status=429)
    who = visitor(request)
    if action == 'like':
        if request.POST.get('liked') == 'true':
            BlogLike.objects.get_or_create(blog=blog, visitor=who)
        else:
            BlogLike.objects.filter(blog=blog, visitor=who).delete()
        return JsonResponse({'liked': blog.likes.filter(visitor=who).exists(), 'likes': blog.likes.count()})
    if action == 'visit':
        source = ''.join(char for char in request.POST.get('source', '').lower()[:80] if char.isalnum() or char in '._-')
        visit, _ = BlogVisit.objects.get_or_create(blog=blog, visitor=who, day=timezone.localdate(), defaults={'source': source})
        if request.POST.get('engaged') == 'true' and not visit.engaged:
            visit.engaged = True
            visit.save(update_fields=['engaged'])
        return JsonResponse({'views': blog.visits.count(), 'likes': blog.likes.count(), 'liked': blog.likes.filter(visitor=who).exists()})
    return JsonResponse({'detail': 'Not found.'}, status=404)

@never_cache
@require_POST
def add_comment(request, pk):
    blog = get_object_or_404(published(), pk=pk)
    if not rate_allowed(request, 'comment', 5):
        return JsonResponse({'detail': 'Please wait before posting another comment.'}, status=429)
    form = TutorialCommentForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    if not form.cleaned_data.get('website'):
        comment = form.save(commit=False)
        comment.blog, comment.approved = blog, False
        comment.save()
    return JsonResponse({'message': 'Thank you! Your comment will appear after approval.'}, status=201)

@login_required
@require_POST
def upload_image(request):
    if not (request.user.has_perm('blogs.add_blog') or request.user.has_perm('blogs.change_blog')):
        return JsonResponse({'detail': 'Permission denied.'}, status=403)
    upload = request.FILES.get('image')
    if not upload or upload.size > 8 * 1024 * 1024:
        return JsonResponse({'detail': 'Choose an image smaller than 8 MB.'}, status=400)
    try:
        image = Image.open(upload)
        if image.width * image.height > 20000000:
            raise ValueError('Image too large')
        image.load()
        image.thumbnail((2400, 2400))
        buffer = io.BytesIO()
        image.convert('RGB').save(buffer, format='JPEG', quality=88)
    except Exception:
        return JsonResponse({'detail': 'Choose a valid PNG, JPEG, GIF, or WebP image.'}, status=400)
    name = default_storage.save('blog_images/inline/' + secrets.token_hex(16) + '.jpg', ContentFile(buffer.getvalue()))
    return JsonResponse({'url': default_storage.url(name)}, status=201)

@login_required
@permission_required('blogs.view_blog', raise_exception=True)
@require_GET
def tutorial_analytics(request):
    return JsonResponse({
        'published': published().count(), 'drafts': Blog.objects.exclude(published_status='Published').count(),
        'views': BlogVisit.objects.count(), 'engaged': BlogVisit.objects.filter(engaged=True).count(),
        'likes': BlogLike.objects.count(), 'pending_comments': BlogComment.objects.filter(approved=False).count(),
        'sources': list(BlogVisit.objects.values('source').annotate(reads=Count('id')).order_by('-reads')[:20]),
        'posts': [{'id': blog.pk, 'title': blog.title, 'status': blog.published_status,
                   'views': blog.view_count(), 'likes': blog.like_count(), 'engaged': blog.engaged_count()}
                  for blog in Blog.objects.all()[:100]],
    })
