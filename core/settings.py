from pathlib import Path
import environ
from firebase_admin import initialize_app


BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(env_file=str(BASE_DIR / ".env"))

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)


INSTALLED_APPS = [
    "modeltranslation",
    "cities_light",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "strawberry.django",
    "strawberry_django",
    "tinymce",
    "fcm_django",
    "api",
    "guard",
    "shared",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", "English"),
    ("fr", "Français"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "upload/"
MEDIA_ROOT = BASE_DIR / "upload"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_CREDENTIALS = True
CORS_PREFLIGHT_MAX_AGE = 86400
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

TINYMCE_DEFAULT_CONFIG = {
    "height": 360,
    "width": "100%",
    "cleanup_on_startup": True,
    "custom_undo_redo_levels": 20,
    "selector": "textarea",
    "plugins": "link lists code",
    "toolbar": "undo redo | bold italic | bullist numlist | link code",
}


CITIES_LIGHT_TRANSLATION_LANGUAGES = ["en", "fr", "ar"]
CITIES_LIGHT_INCLUDE_COUNTRIES = ["TN", "MA", "DZ", "LY", "EG", "LB", "YE", "SY"]
CITIES_LIGHT_INCLUDE_CITY_TYPES = ["PPL", "PPLA", "PPLA2", "PPLA3", "PPLA4", "PPLC"]

LOGIN_URL = "shared:login"
LOGIN_REDIRECT_URL = "guard:dashboard"
LOGOUT_REDIRECT_URL = "shared:login"

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
ADMIN_LIST_EMAILS = env.list("ADMIN_LIST_EMAILS")


if DEBUG:
    SITE_URL = "http://localhost:8000"
    CORS_ALLOW_ALL_ORIGINS = DEBUG
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

    STATICFILES_DIRS = [
        BASE_DIR / "static",
    ]


else:
    SITE_URL = env("SITE_URL")
    CORS_ALLOWED_ORIGINS = [
        "https://fielmedina.com",
        "https://www.fielmedina.com",
    ]
    ALLOWED_HOSTS = ["mystory.fielmedina.com"]
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = env("EMAIL_HOST")
    EMAIL_PORT = env.int("EMAIL_PORT")
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
    EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASSWORD"),
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT"),
        }
    }
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    STATIC_ROOT = BASE_DIR / "static"


PUBLIC_GROQ_API_KEI = env("PUBLIC_GROQ_API_KEI")
PUBLIC_SHORT_API = env("PUBLIC_SHORT_API")
SHORT_IO_DOMAIN = env("SHORT_IO_DOMAIN")
SHORT_IO_FOLDER_ID = env("SHORT_IO_FOLDER_ID")
DJANGO_ADMIN_URL = env("DJANGO_ADMIN_URL")

FIREBASE_APP = initialize_app()

GOOGLE_APPLICATION_CREDENTIALS = env("GOOGLE_APPLICATION_CREDENTIALS")

FCM_DJANGO_SETTINGS = {
    "APP_VERBOSE_NAME": "FielMedina",
    "ONE_DEVICE_PER_USER": False,
    "DELETE_INACTIVE_DEVICES": False,
    "UPDATE_ON_DUPLICATE_REG_ID": True,
}
