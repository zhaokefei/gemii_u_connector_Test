# -*- coding:utf-8 -*-
"""
Django settings for UConnector project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import pymysql
pymysql.install_as_MySQLdb()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b@%h+42m$vqj)ms3%l3a86p*72&6(lo)!w_(skg8qu%k0uv%wv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['52.80.5.112', 'jbb.gemii.cc']
# APPEND_SLASH = False

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'connector',
    'wechat',
    'wyeth',
    'legacy_system',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

NO = '201705051010001'
SEC = '201705051010001'
UC_AGENT = 'oc1cx1MixijF8PgdqN9kL3yVKpZo'

ROOT_URLCONF = 'UConnector.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'UConnector.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'u_connector',
        'USER': 'root',
        'PASSWORD': 't721si74',
        'HOST': 'wechatbot4jbb.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn',
        'PORT': '3306',
        'OPTIONS': {
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                    'charset': 'utf8mb4',
        },
    },

    'gemii_b': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wechat_gemii',
        'USER': 'root',
        'PASSWORD': 't721si74',
        'HOST': 'wechatbot4jbb.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    },

    'gemii': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wechat',
        'USER': 'root',
        'PASSWORD': 't721si74',
        'HOST': 'wechat4bot.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    },

    'wyeth_b': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wechat4bot2hye',
        'USER': 'root',
        'PASSWORD': 't721si74',
        'HOST': 'wechatbot4jbb.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    },
    'wyeth': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wechat',
        'USER': 'root',
        'PASSWORD': 't721si74',
        'HOST': 'wechat4bot2wyeth.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    },
}

REDIS_CONFIG = {
    'redis_a': {
        'host': '54.223.132.253',
        'port': '8081',
        'password': 'gemii@123.cc',
        'db': 0,
        'type': 'A'
    },
    'redis_b': {
        'host': 'gemii-jbb.ldtntv.ng.0001.cnn1.cache.amazonaws.com.cn',
        'port': '6379',
        'password': '',
        'db': 0,
        'type': 'B'
    },
}

CALLBACK_JAVA = "http://jbb.gemii.cc/GroupManage/file/updateInfo"

DATABASE_ROUTERS = ['UConnector.router.AuthRouter']


# TODO 缓存设置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://:gemii@123.cc@54.223.132.253:8081/1",
    },
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(process)d - [%(levelname)s] [%(asctime)s] - [%(pathname)s:%(lineno)d] - %(message)s',
            'datefmt' : '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'view': {
            'handlers': ['view_error_handler'],
            'level': 'INFO',
            'propagate': True,
        },
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'view_error_handler': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/view.error.log',
            'formatter': 'verbose',
        },
        'info_handler': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/info.log',
            'formatter': 'verbose',
        },
        'error_handler': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
            'formatter': 'verbose',
        },
        'task_info_handler': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/task.info.log',
            'formatter': 'verbose',
        },
        'task_error_handler': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/task.error.log',
            'formatter': 'verbose',
        },
        'sql_info_handler': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/sql.info.log',
            'formatter': 'verbose',
        },
        'sql_error_handler': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/sql.error.log',
            'formatter': 'verbose',
        },
        'send_message_handler': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/messaga.info.log',
            'formatter': 'verbose',
        },
        'send_message_error_handler': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/messaga.error.log',
            'formatter': 'verbose',
        },
        'member_handler': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/member.info.log',
            'formatter': 'verbose',
        },
        'member_error_handler': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/member.error.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['info_handler', 'error_handler'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.task': {
            'handlers': ['task_info_handler', 'task_error_handler'],
            'level': 'INFO',
            'propagate': True,
        },
        'celery': {
            'handlers': ['task_info_handler', 'task_error_handler'],
            'level': 'INFO',
            'propagate': True,
        },
        'sql': {
            'handlers': ['sql_info_handler', 'sql_error_handler'],
            'level': 'INFO',
            'propagate': True,
        },
        'message': {
            'handlers': ['send_message_handler', 'send_message_error_handler'],
            'level': 'INFO',
            'propagate': True,
        },
        'member': {
            'handlers': ['member_handler', 'member_error_handler'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}



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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# upload folder
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

