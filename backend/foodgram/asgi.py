import os

from django.core.asgi import get_asgi_application


# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')

# Create the ASGI application
application = get_asgi_application()
