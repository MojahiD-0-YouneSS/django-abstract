from typing import Optional, List, Any, Union
from django.db.models import Model, QuerySet
from django.apps import apps
from datetime import datetime
from abc import ABC
from django_abstract.utilities import ClassInfoProvider


class_info_provider = ClassInfoProvider()

class GenericCreator:
    """A generic creator class for Django models.

    Attributes:
        model_rep (str): String representation of the model or model class name.
        model (Model): The actual Django model class.
        creator_info (dict): Class information for the creator.
    """
    def __init__(self, model_rep: str = None, is_model=True):
        """Initialize the GenericCreator.

        Args:
            model_rep (str, optional): The model class or string representation (e.g., 'myapp.MyModel'). Defaults to None.
            is_model (bool, optional): True if model_rep is the model class, False if it's a string. Defaults to True.
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

    def deactivated_by(self, name, is_get_or_create: bool = False, action='create') -> Optional[QuerySet]:
        """Create or get records by deactivated_by user.

        Args:
            name: The user or name who deactivated the record.
            is_get_or_create (bool, optional): Whether to use get_or_create instead of create. Defaults to False.
            action (str, optional): Action type. Defaults to 'create'.

        Returns:
            Optional[QuerySet]: The resulting queryset or created object.
        """
        return self._cleaned_hundler(is_get_or_create=is_get_or_create,action=action,deactivated_by=name)
        

    def created_by(self, name, is_get_or_create: bool = False, is_model: bool = False) -> Union[Optional[QuerySet], Any]:
        """Get records by creator.

        Args:
            name: The creator's name or user object.
            is_get_or_create (bool, optional): Whether to use get_or_create. Defaults to False.
            is_model (bool, optional): Return a queryset if True. Defaults to False.

        Returns:
            Union[Optional[QuerySet], Any]: Single record or queryset.
        """
        return self._cleaned_hundler(is_get_or_create=is_get_or_create,action=action,created_by=name)
        

    def updated_by(self, name, is_get_or_create: bool = False, is_model: bool = False) -> Union[Optional[QuerySet], Any]:
        """Get records by last updater.

        Args:
            name: The updater's name or user object.
            is_get_or_create (bool, optional): Return a queryset if True. Defaults to False.
            is_model (bool, optional): Return a queryset if True. Defaults to False.

        Returns:
            Union[Optional[QuerySet], Any]: Single record or queryset.
        """
        return self._cleaned_hundler(is_get_or_create=is_get_or_create,action=action,updated_by=name)
        
