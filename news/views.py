
from django.shortcuts import render,  redirect
from.models import NewsArticle
from core.views import paginate

def news_list_visitor(request):
    news_articles = NewsArticle.objects.all()
    
    news_articles_list = paginate( news_articles, 12, request)

    return render(request, 'front/news.html', {'news_articles': news_articles_list})

def news_detail(request, news_id):
    try:
        news_item = NewsArticle.objects.get(id=news_id)
    except Exception as e:
        # Handle the case where the news with the provided ID does not exist
        return redirect("news_list_visitor")

    

    return render(request, 'front/news_detail.html', {
        'news_item': news_item, 
        'lastnews':NewsArticle.objects.exclude(id = news_item.id)
        
    })
