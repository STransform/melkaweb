from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib.syndication.views import Feed
from django.utils.html import escape
from core.presentation import render
from .tutorials import published, article_data, library_data, add_comment

class TutorialList(View):
    def get(self, request):
        return render(request, 'front/blog.html', {'tutorial_library': library_data(request), 'blog_page': True})

class TutorialDetail(View):
    def get(self, request, blog_id=None, slug=None):
        blog = get_object_or_404(published(), **({'pk': blog_id} if blog_id else {'slug': slug}))
        if blog_id:
            return redirect(blog.get_absolute_url(), permanent=True)
        data = article_data(blog, request)
        data['comments'] = [{**item, 'created_at': item['created_at'].isoformat()} for item in blog.comments().values('author', 'message', 'created_at')]
        related = published().exclude(pk=blog.pk)
        if blog.blog_category_id:
            related = related.filter(blog_category_id=blog.blog_category_id)
        data['related'] = [article_data(item, request, False) for item in related[:3]]
        data['lessons'] = [article_data(item, request, False) for item in published().filter(series=blog.series).order_by('series_order', 'pk')] if blog.series else []
        return render(request, 'front/blog_detail.html', {'tutorial': data, 'blog_page': True})
    def post(self, request, blog_id=None, slug=None):
        blog = get_object_or_404(published(), **({'pk': blog_id} if blog_id else {'slug': slug}))
        return add_comment(request, blog.pk)

class TutorialFeed(Feed):
    title = 'MelkaTech Tutorials'
    link = '/tutorials/'
    description = 'Practical tutorials on software, DevOps, cloud and security.'
    def items(self):
        return published()[:25]
    def item_title(self, item):
        return item.title
    def item_description(self, item):
        return escape(item.summary or item.title)
    def item_pubdate(self, item):
        return item.published_at or item.created_date

def tutorial_sitemap(request):
    entries = ''.join(f'<url><loc>{escape(request.build_absolute_uri(item.get_absolute_url()))}</loc><lastmod>{item.updated_at.date().isoformat()}</lastmod></url>' for item in published())
    return HttpResponse('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + entries + '</urlset>', content_type='application/xml')
