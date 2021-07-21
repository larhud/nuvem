# -*- coding: utf-8 -*-
from larhud.settings import *

DEBUG = False

for template_config in TEMPLATES:
    template_config['OPTIONS']['debug'] = DEBUG

SITE_NAME = '%(titulo)s'
SITE_HOST = 'http://%(host)s'

GOOGLE_RECAPTCHA_PUBLIC_KEY = ''
GOOGLE_RECAPTCHA_SECRET_KEY = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '%(dbname)s',
        'USER': '%(dbuser)s',
        'PASSWORD': '%(dbpassword)s',
        'HOST': '%(dbhost)s',
        'PORT': '',
    },
}

ALLOWED_HOSTS = ['%(host)s', 'www.%(host)s', ]

REPLY_TO_EMAIL = 'ppgci@eco.ufrj.br'
DEFAULT_FROM_EMAIL = 'ppgci@eco.ufrj.br'

# A API Key para detecção da linguagem pode ser obtida em https://detectlanguage.com/
API_KEY_LANGUAGE = ''

# Local onde se encontram os tipos de fontes das letras da nuvem
# Se vc não especificar, a rotina ira utilizar as fontes localizadas em
FONT_PATH=''
