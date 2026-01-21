# core/base_selector.py
from typing import Iterable
#from django.db import models
from django.db.models.query import QuerySet , ValuesIterable, ValuesListIterable
from django_abstract.generic.generic_selectors import (GenericSelector,)
from django_abstract.utilities import ClassInfoProvider

class BaseSelector(GenericSelector):
    def __init__(self, model_class):
        self.model_class = model_class
        self.selector_data = ClassInfoProvider().resolve_class_info(obj=self)
    @property
    def access_db(self):
       return self.model_class.objects
   