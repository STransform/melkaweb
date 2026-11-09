import os
from pathlib import Path
from decouple import config
from django.contrib.admin.options import ModelAdmin as DEFAULT_MODEL_ADMIN

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8001',
    'http://127.0.0.1:8001',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://localhost.com', 
    'https://melkaa.com',
    'https://www.melkaa.com',
]
CSRF_TRUSTED_ORIGINS += [
    origin.strip() for origin in config('FRONTEND_ORIGINS', default='').split(',')
    if origin.strip()
]

# lists of allowed hosts
ALLOWED_HOSTS = ['melkaa.com', 'www.melkaa.com','127.0.0.1','localhost']
USE_X_FORWARDED_HOST = True
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG

# Application definition

INSTALLED_APPS = [
   
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'about_us',
    'documents',
    'news',
    'suppliers',
    'vacancies',
    'dashboard',
    'task_manager',
    'blogs',
    'accounts',
    'core',
    'visit_counter', #Track user visits
    'services',
    

    # 'jazzmin',
    'djangocms_admin_style',
    'modeltranslation', # dynamic translation
    'django.contrib.admin', 
     
    # cms
    "django.contrib.sites",
    "cms",
    "menus",
    "treebeard",
    
    "sekizai",
    'djangocms_alias',
    # 'djangocms_versioning',
    
    'filer',
    'easy_thumbnails',

    # cms packages
    'djangocms_text_ckeditor',
    "djangocms_frontend",
    "djangocms_frontend.contrib.accordion",
    "djangocms_frontend.contrib.alert",
    "djangocms_frontend.contrib.badge",
    "djangocms_frontend.contrib.card",
    "djangocms_frontend.contrib.carousel",
    "djangocms_frontend.contrib.collapse",
    "djangocms_frontend.contrib.content",
    "djangocms_frontend.contrib.grid",
    "djangocms_frontend.contrib.image",
    "djangocms_frontend.contrib.jumbotron",
    "djangocms_frontend.contrib.link",
    "djangocms_frontend.contrib.listgroup",
    "djangocms_frontend.contrib.media",
    "djangocms_frontend.contrib.tabs",
    "djangocms_frontend.contrib.utilities",

    "djangocms_file",
    "djangocms_picture",
    "djangocms_video",
    "djangocms_googlemap",
    "djangocms_snippet",
    "djangocms_style",
    "crispy_forms",
    'rosetta', #For generating language translating dashboard
    "crispy_bootstrap5",
    
    
]

CUSTOM_INSTALLED_APPS = [
    'about_us',
    'documents',
    # 'news',
    #'suppliers',
    'vacancies',
    'dashboard',
    #'task_manager',
    'blogs',
    'accounts',
    'core',
]

#  to process requests and responses before and after they reach the view.
MIDDLEWARE = [
    'core.presentation.PresentationMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'visit_counter.middleware.UserVisitMiddleware',
    
    # cms
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    
]

ROOT_URLCONF = 'malkaa.urls'

# template directory
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')] if os.path.exists(os.path.join(BASE_DIR, 'templates')) else [],
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'core.presentation.PresentationTemplateLoader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.stgs',
                # cms
                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
                
            ],
        },
    },
]


THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

# specifies the full path to the Django's runserver command
WSGI_APPLICATION = 'malkaa.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='melkaanm_db'),
        'USER': config('DB_USER', default='melkaanm_user'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='3306'),
        # MySQL's legacy utf8/utf8mb3 connection encoding rejects emoji even
        # when the database and content columns already use utf8mb4.
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

# password validator
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# default language
LANGUAGE_CODE = 'en'

# other languages
LANGUAGES = [
    ('en', ('English')),
    ('ax', ('Amharic')),
    ('ox', ('Afaan Oromoo')),
    
]


# Our custom languages used in Ethiopia, not defined by Django
EXTRA_LANG_INFO = {
    'ax': {
        'bidi': False, # right-to-left
        'code': 'ax',
        'name': 'አማርኛ',
        'name_local': u'አማርኛ',
    },
    'ox': {
        'bidi': False, # right-to-left
        'code': 'ox',
        'name': 'Afaan Oromoo',
        'name_local': u'Afaan Oromoo',
    },
    
    
}

# Add custom languages not provided by Django
import django.conf.locale
LANG_INFO = dict(django.conf.locale.LANG_INFO, **EXTRA_LANG_INFO)
django.conf.locale.LANG_INFO = LANG_INFO


## Settings for model translation
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_LANGUAGES = ('en','ax','ox') 
MODELTRANSLATION_ENABLE_FALLBACKS = True
MODELTRANSLATION_FALLBACK_LANGUAGES = ('en',)


LOCALE_PATHS = [ os.path.join(BASE_DIR,'locale'), ]

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True

USE_TZ = True

GRAPH_MODELS ={
    'all_applications': True,
    'graph_models': True,
    }

# static
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [BASE_DIR, "static"]

# media
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# settings.py

AUTH_USER_MODEL = 'accounts.UserProfile'

AUTHENTICATION_BACKENDS = [
    'accounts.backends.FlexibleModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# send email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'stemesgent@gmail.com'
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_FROM = 'Simon <stemesgent@gmail.com>'

# Package settings

## cms settings
SITE_ID = 1

# cms template settings
CMS_TEMPLATES = (
    ("front/cms_bases/cms_base.html", ("Cms Base Template")),
    ("front/cms_bases/cms_home_base.html", ("Homepage Template")),
)


CMS_CONFIRM_VERSION4 = True
# Pages are data responses to Next.js; never reuse an old rendered-page cache.
CMS_PAGE_CACHE = False
# Allow admin sidebar to open admin URLs | Allow embedding from the same origin
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Enable inline editing with djangocms-text-ckeditor
# https://github.com/django-cms/djangocms-text-ckeditor#inline-editing-feature
TEXT_INLINE_EDITING = True
THUMBNAIL_HIGH_RESOLUTION = True
THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)

INTERNAL_IPS = ["127.0.0.1",]

DJANGOCMS_VERSIONING_ALLOW_DELETING_VERSIONS = True

## Roseta settings
ROSETTA_MESSAGES_PER_PAGE = 100

CORS_ORIGIN_ALLOW_ALL = True
CSP_MIDDLEWARE = [
    'csp.middleware.CSPMiddleware',

]

# Allow resources from the same origin
CSP_DEFAULT_SRC = ("'self'",)  

# Allow embedding from specific domains
CSP_FRAME_SRC = ("'self'",)

# implement the search field for filer package 
DEFAULT_MODEL_ADMIN.search_fields = ['']

## Security Settings

# A custom setting to set maximum allowed concurrent session for a user
MAX_ALLOWED_CONCURRENT_SESSIONS = 2

SESSION_MINS = 60 # The length of minutes for user sessions to expire
SESSION_COOKIE_AGE = SESSION_MINS * 60 # Expire user sessions after 30 mins
SESSION_EXPIRE_AT_BROWSER_CLOSE = True # Logout if the user closes the browser

# After SSL is configured
# SECURE_SSL_REDIRECT = True # Redirect all requests to SSl
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True # Use ssl for subdomains too
# CSRF_COOKIE_SECURE = True # No csrf for http requests
# SESSION_COOKIE_SECURE = True # No Session for http request

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"
