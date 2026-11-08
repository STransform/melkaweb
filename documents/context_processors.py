from .models import Document
def document_data(request):
    # Fetch documents from the Document model and group them by category
    document_categories = {}
    for category, _ in Document.CATEGORY_CHOICES:
        documents = Document.objects.filter(category=category)
        document_categories[category] = documents

    # Return the document data as a dictionary
    return {'document_categories': document_categories}
