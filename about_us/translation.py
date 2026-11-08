from modeltranslation.translator import register,TranslationOptions
from .models import About, TeamMember, BureauStructure, Service, Technology,Infrastructure,Innovation,CompanyValues,VisionMission,Vision,OtechExcellence,WhatPeopleSays,AboutOtechFooter,ElevatingSkills 

@register(About)
class AboutTranslationOption(TranslationOptions):
    fields = ('title',"content", "mission", "vision", "values")

@register(TeamMember)
class TeamMemberTranslationOption(TranslationOptions):
    fields = ('name', 'role' )

@register(BureauStructure)
class StructureTranslationOption(TranslationOptions):
    fields = ('title', 'content', 'management_board_title', 'management_board_content', 'execution_team_title', 'execution_team_content')


@register(Service)
class ServiceTranslationOption(TranslationOptions):
    fields = ('title', 'content')


@register(Technology)
class TechnologyTranslationOption(TranslationOptions):
    fields = ('title', 'content')

@register(Infrastructure)
class InfrastructureTranslationOption(TranslationOptions):
    fields = ('infr_title', 'infr_content')

@register(Innovation)
class InnovationTranslationOption(TranslationOptions):
    fields = ('invn_title', 'invn_content')
@register(CompanyValues)
class CompanyValuesTranslationOption(TranslationOptions):
    fields = ('title', 'content')

@register(VisionMission)
class VisionMissionTranslationOption(TranslationOptions):
    fields = ('title', 'content')
@register(Vision)
class VisionTranslationOption(TranslationOptions):
    fields = ('title', 'content')

@register(OtechExcellence)
class OtechExcellenceTranslationOption(TranslationOptions):
    fields = ('title1', 'content1','title2','content2','title3','content3')

@register(WhatPeopleSays)
class WhatPeopleSaysTranslationOption(TranslationOptions):
    fields = ('content','full_name','position')

@register(AboutOtechFooter)
class AboutOtechFooterTranslationOption(TranslationOptions):
    fields = ('title','content')
@register(ElevatingSkills)
class ElevatingSkillsTranslationOption(TranslationOptions):
    fields = ('title','content')