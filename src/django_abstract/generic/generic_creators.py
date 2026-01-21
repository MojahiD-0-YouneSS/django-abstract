from typing import Optional, List, Any, Union
from django.db.models import Model, QuerySet
from django_abstract.base_selector import BaseSelector
from django.apps import apps
from datetime import datetime
from abc import ABC
from django_abstract.utilities import ClassInfoProvider


class_info_provider = ClassInfoProvider()

class GenericCreator:
    def __init__(self,model_rep: str = None,is_model=True,):
        """
        A generic selector for Django model fields
        Args:
            dependency: Related model for lookups
            model: Target model for selection a class or a string as 'myapp.MyModel'
            
        """
        self.model_rep = str(model_rep)
        self.model:Optional[Model] = self.model_rep if is_model else apps.get_model(self.model_rep)
        self.creator_info = class_info_provider.resolve_class_info(obj=self)

    def _cleaned_hundler(self,is_get_or_create: bool = False, action='create',**kwargs):
        if self.model:
            if is_get_or_create:
                queryset = self.model.objects.create(**kwargs)
            else:
                queryset = self.model.objects.get_or_create(**kwargs)
        
        return queryset if queryset else None

    def deactivated_by(self,name, is_get_or_create: bool = False, action='create') -> Optional[QuerySet]:
        """
        Get deactivated records
        Args:
            date_value: Datetime threshold
            is_model: Return a queryset if True
        Returns:
            Queryset of (in)active records
        """
        return self._cleaned_hundler(is_get_or_create=is_get_or_create,action=action,deactivated_by=name)
        

    def created_by(self, name, is_get_or_create:bool=False, is_model:bool=False) -> Union[Optional[QuerySet], Any]:
        """
        Get records by creator
        Args:
            is_get_or_create: Return a queryset if True
            is_model: Return a queryset if True        Returns:
            Single record or queryset
        """
        return self._cleaned_hundler(is_get_or_create=is_get_or_create,action=action,created_by=name)
        

    def updated_by(self,name, is_get_or_create:bool=False, is_model:bool=False) -> Union[Optional[QuerySet], Any]:
        """
        Get records by last updater
        Args:
            is_list: Return a queryset if True
            is_model: Return a queryset if True
        Returns:
            Single record or queryset
        """
        return self._cleaned_hundler(is_get_or_create=is_get_or_create,action=action,updated_by=name)
        
