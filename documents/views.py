import os
from django.shortcuts import render
from .models import Document
from django.http import FileResponse
from django.conf import settings

from core.views import paginate

def list_docs_view(request):
    documents = Document.objects.all()
    categories = Document.CATEGORY_CHOICES
    documents_by_category = {}
    for category, _ in categories:
        documents_by_category[category] = Document.objects.filter(category=category)


    documents_list = paginate( documents, 10, request)

    context = {
        'categories': categories,
        'documents_by_category': documents_by_category,
        'documents':documents_list,
    }
    
    return render(request, 'front/docs.html', context)

def pdf_view(request, pk):
    try:
        url='documents/' + pk
        file_path = os.path.join(settings.MEDIA_ROOT, url)

        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    
    except Exception as e:
        print(f"Exception while rendering document file with id {pk} :" ,e)
