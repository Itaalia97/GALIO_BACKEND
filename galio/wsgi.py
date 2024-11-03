"""
WSGI config for galio project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys

# Agrega la ruta del proyecto y del entorno virtual
sys.path.append('/home/galio/GALIO_BACKEND')
sys.path.append('/home/galio/.pyenv/versions/galio/lib/python3.8/site-packages')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'galio.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
