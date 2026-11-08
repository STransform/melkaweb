from .models import Settings, Pages
from dashboard.models import QuickLink, Contact
from visit_counter.models import UserVisit

def stgs(request):
    quick_links = QuickLink.objects.all()
    contact = Contact.objects.all()
    pages = Pages.objects.first()
    vc = UserVisit.objects.count()
    vcn_list = ["","K","M","B"]
    l, index = len(str(vc)), 0
    if 4 <= l <= 6: index = 1
    elif 7 <= l <= 9 : index = 2
    elif l > 10: index = 3
    
    reduced_vc = vc/pow(1000, index)
    vc_name = vcn_list[index] 

    return {
        'quick_links': quick_links,  # Include footer data in context
        'contact': contact,
        'stg':Settings.objects.first(),
        'pages': pages,
        'visitors':reduced_vc,
        'visitors_round':vc_name
    }

