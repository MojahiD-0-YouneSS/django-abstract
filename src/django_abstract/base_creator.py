# core creators.py

from  django.db import  IntegrityError, transaction
from django_abstract.utilities import ClassInfoProvider
from django_abstract.generic.generic_creators import GenericCreator


class BaseCreator(GenericCreator):
    def __init__(self, model_class):
        self.model_class = model_class
        self.status=False
        self.system_infos = ClassInfoProvider().resolve_class_info(obj=self)
        super().__init__(model_rep=model_class)
    @property
    def access_db(self):
       return self.model_class.objects
