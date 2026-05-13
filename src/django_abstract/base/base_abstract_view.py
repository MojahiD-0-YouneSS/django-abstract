from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ImproperlyConfigured
from django_abstract.utilities import (
    EntryBindingMixin,
)

class AbstractViewClass(EntryBindingMixin, View):
    """
    Standard Base View for GMES-enabled endpoints."""
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
