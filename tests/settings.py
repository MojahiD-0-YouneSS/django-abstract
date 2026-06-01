import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# This is a fake Django settings file just for running Pytest
SECRET_KEY = 'fake-key-for-testing-only'
DEBUG = True
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django_abstract',
    'tests',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:', # Runs instantly in RAM
    }
}
