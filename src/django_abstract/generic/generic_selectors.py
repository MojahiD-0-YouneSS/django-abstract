from typing import Optional, List, Any, Union
from django.db.models import Model, QuerySet
from django.apps import apps
from datetime import datetime
from django_abstract.utilities import ClassInfoProvider

class GenericSelector:
    """A generic selector for Django model fields.

    Attributes:
        model_str_rep (str): String representation of the model.
        model (Model): The target Django model class.
        creator_info (dict): Resolved class information for the selector.
    """
    def __init__(self, model_rep: str = None, is_model=True):
        """Initialize the GenericSelector.

        Args:
            model_rep (str, optional): Target model class or string representation. Defaults to None.
            is_model (bool, optional): True if model_rep is a model class, False if string. Defaults to True.
        """
        self.model_str_rep = str(model_rep)
        self.model:Optional[Model] = model_rep if is_model else apps.get_model(self.model_str_rep)
        self.creator_info = ClassInfoProvider.resolve_class_info(obj=self)

    def ids(self, is_list: bool = False, value: Optional[int] = None) -> Union[Optional[int], QuerySet]:
        """Get ID(s) based on conditions.

        Args:
            is_list (bool, optional): If True, returns a flat queryset of all IDs. Defaults to False.
            value (int, optional): Specific ID to lookup if is_list is False. Defaults to None.

        Returns:
            Union[Optional[int], QuerySet]: Single instance or queryset of IDs.
        """
        try:
            if  is_list:
                return self.model.objects.values_list('id', flat=True)
            else:
                return self.model.objects.filter(id=value).first()
        except :
            pass

    def created_at(self, date_value: Optional[datetime] = None) -> Union[Optional[QuerySet], Any]:
        """Get records by created_at timestamps.

        Args:
            date_value (datetime, optional): Optional date filter. Defaults to None.

        Returns:
            Union[Optional[QuerySet], Any]: Filtered queryset or specific timestamp.
        """
        try:
            if date_value and self.model:
                queryset = self.model.objects.filter(created_at=date_value)
            return queryset if queryset else None
        except:
            pass

    def updated_at(self, date_value: Optional[datetime] = None,) -> Optional[QuerySet]:
        """
        Get records updated since specific time
        Args:
            date_value: Datetime threshold
            is_model: Return a queryset if True
        Returns:
            Queryset of updated records
        """
        try:
            if date_value and self.model:
                queryset = self.model.objects.filter(updated_at=date_value)
            return queryset if queryset else None
        except:pass
        
    def deactivated_at(self, date_value: Optional[datetime] = None,) -> Optional[QuerySet]:
        """
        Get deactivated records
        Args:
            date_value: Datetime threshold
            is_model: Return a queryset if True
        Returns:
            Queryset of (in)active records
        """
        try:
            if date_value and self.model:
                queryset = self.model.objects.filter(deactivated_at=date_value)
            return queryset if queryset else None
        except:pass
        
    def deactivated_by(self, date_value: Optional[datetime] = None,) -> Optional[QuerySet]:
        """
        Get deactivated records
        Args:
            date_value: Datetime threshold
            is_model: Return a queryset if True
        Returns:
            Queryset of (in)active records
        """
        try:
            if date_value and self.model:
                queryset = self.model.objects.filter(deactivated_by=date_value)
            return queryset if queryset else None
        except:pass
        
    def is_active(self, active: bool = True,) -> Optional[QuerySet]:
        """
        Filter by active status
        Args:
            active: True for active, False for inactive
            is_model: Return a queryset if True
        Returns:
            Queryset of active/inactive records
        """
        try:
            if self.model:
                queryset = self.model.objects.filter(is_active=active)
            return queryset if queryset else None
        except:pass
        
    def is_disabled(self, disabled: bool = True,) -> Optional[QuerySet]:
        """
        Filter by disabled status
        Args:
            disabled: True for disabled, False for enabled
            is_model: Return a queryset if True
        Returns:
            Queryset of disabled/enabled records
        """
        try:
            if self.model:
                queryset = self.model.objects.filter(is_disabled=disabled)
            return queryset if queryset else None
        except:pass
        
    def created_by(self, is_list:bool=False,) -> Union[Optional[QuerySet], Any]:
        """
        Get records by creator
        Args:
            is_list: Return a queryset if True
            is_model: Return a queryset if True        Returns:
            Single record or queryset
        """
        try:
            if is_list:
                queryset = self.model.objects.values_list("created_by")
            else:
                queryset = self.model.objects.values_list("created_by").first()
            return queryset if queryset else None
        except:
            pass

    def updated_by(self, is_list:bool=False,) -> Union[Optional[QuerySet], Any]:
        """
        Get records by last updater
        Args:
            is_list: Return a queryset if True
            is_model: Return a queryset if True
        Returns:
            Single record or queryset
        """
        try:
            if is_list:
                queryset = self.model.objects.values_list("updated_by")
            else:
                queryset = self.model.objects.values_list("updated_by").first()
            return queryset if queryset else None
        except:
            pass
