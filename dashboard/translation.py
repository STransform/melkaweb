from .models import *
from modeltranslation.translator import TranslationOptions, register

@register(GalleryCategory)
class GalleryCategoryTO(TranslationOptions):
    fields = ("name",)


@register(GalleryImage)
class GalleryImageTO(TranslationOptions):
    fields = ("title",)


@register(DirectorateMessage)
class  DirectorateMessageTO(TranslationOptions):
    fields = ("title","content")

@register(FeaturedWork)
class  FeaturedWorkTO(TranslationOptions):
    fields = ("title","description")
@register(TechnologyService)
class  TechnologyServiceTO(TranslationOptions):
    fields = ("title","description")

@register(FAQ)
class  FAQTO(TranslationOptions):
    fields = ("question","answer")

@register(QuickLink)
class  QuickLinkTO(TranslationOptions):
    fields = ("title","url")

@register(Event)
class EventTO(TranslationOptions):
    fields = ("title","location", "description")


@register(Bid)
class BidTO(TranslationOptions):
    fields = ("title","description")




