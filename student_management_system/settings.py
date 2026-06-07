
import os
from dotenv import load_dotenv
from numpy import False_


load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY =os.environ.get('SECRET_KEY')
SECRET_KEY = os.getenv("SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1','*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_comments_xtd',
    'django_comments',

     'rest_framework',

    "widget_tweaks",
    'crispy_forms',
    'crispy_bootstrap4',
    'slick_reporting',


    'student_core',
    'student_account',
    'student_result',
    'student_exam',
    'library',
    'bookstore',
    'search.apps.SearchConfig',
    'order',
    'cart',
    'school',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap4'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

SITE_ID = 1

COMMENTS_XTD_SALT = (b"Timendi causa est nescire. "
                     b"Aequam memento rebus in arduis servare mentem.")
COMMENTS_APP = "django_comments_xtd"
# Source mail address used for notifications.
COMMENTS_XTD_FROM_EMAIL = "kingpo777@gmail.com"

# Contact mail address to show in messages.
COMMENTS_XTD_CONTACT_EMAIL =  os.environ.get('ADMIN_EMAIL')

#COMMENTS_XTD_API_GET_USER_AVATAR = "eyeson.utils.get_avatar_url"

COMMENTS_XTD_APP_MODEL_OPTIONS = {
    'student_exam.assignment': {
        'allow_flagging': True,
        'allow_feedback': True,
        'show_feedback': True,
        'who_can_post': 'users'  # Valid values: 'all', users'
    }
}


# Email Sending
if not DEBUG:

    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT =False
    SESSION_COOKIE_SECURE=True

    SERVER_EMAIL =  os.environ.get('ADMIN_EMAIL')
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST_USER = SERVER_EMAIL
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_PASSWORD = "fkcxonqkrlkkhqoh"
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
    ACCOUNT_EMAIL_VERIFICATION = 'none'
else:
    EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend")
    SECURE_SSL_REDIRECT = False

COMMENTS_XTD_MAX_THREAD_LEVEL = 1
COMMENTS_XTD_CONFIRM_EMAIL = False

COMMENTS_XTD_LIST_ORDER = ('-thread_id', 'order')


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'student_core.middleware.SiteWideConfigs',

    # 'student_core.LoginCheckMiddleWare.LoginCheckMiddleWare',
]


ROOT_URLCONF = 'student_management_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "student_core.context_processors.site_defaults",
                'bookstore.context_processors.bookcategory',
                'bookstore.context_processors.cart',
            ],
        },
    },
]

WSGI_APPLICATION = 'student_management_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.sqlite3',
         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
     }
  #    'default' : {
  #      'ENGINE': 'django.db.backends.postgresql_psycopg2',
  #      'NAME':  os.environ.get('DB_NAME'),
  #      'USER':  os.environ.get('DB_USER'),
  #      'PASSWORD': os.environ.get('DB_PASSCODE'),
  #      'HOST': 'localhost',
  #      'PORT': '',
  #  }
    #   'default' : {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'cpihstje',
    #     'USER': 'cpihstje',
    #     'PASSWORD': 'HGUDEym3spUCcPbcXvTkQBFpgByIgP2i',
    #     'HOST': 'rogue.db.elephantsql.com',
    #     'PORT': '',
    # }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CART_SESSION_ID = 'cart'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [ os.path.join(BASE_DIR, 'static'),]
#STATICFILES_DIRS = [ os.path.join(BASE_DIR, ''),]
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'



#For Custom USER
AUTH_USER_MODEL = "student_core.CustomUser"

# Registering Custom Backend "EmailBackEnd"
AUTHENTICATION_BACKENDS = ['student_core.EmailBackEnd.EmailBackEnd']
