# core/base_selector.py
from typing import Iterable
#from django.db import models
from django.db.models.query import QuerySet , ValuesIterable, ValuesListIterable
from django_abstract.generic.generic_selectors import (GenericSelector,)
from django_abstract.utilities import ClassInfoProvider

class BaseSelector(GenericSelector):
    """Base selector class for abstracting database query operations.

    Attributes:
        model_class (Type[Model]): The Django model class to query.
        selector_data (dict): Resolved class information for logging/metadata.
    """

    def __init__(self, model_class):
        """Initialize the BaseSelector with a specific model class.

        Args:
            model_class (Type[Model]): The Django model class.
        """
        self.model_class = model_class
        self.selector_data = ClassInfoProvider().resolve_class_info(obj=self)

    @property
    def access_db(self):
        """Access the default manager of the model class.

        Returns:
            Manager: The default Django model manager (e.g., objects).
        """
        return self.model_class.objects

    def get_by(self, **kwargs):
        """Retrieve a single record matching the given keyword arguments.

        Args:
            **kwargs: Filter arguments.

        Returns:
            Model: The matching model instance.

        Raises:
            Exception: Re-raises any exception encountered during the query (e.g., ObjectDoesNotExist, MultipleObjectsReturned).
        """
        try:
            return self.access_db.get(**kwargs)
        except Exception as e:
            raise e

    def filter_by(self, **kwargs):
        """Retrieve multiple records matching the given keyword arguments.

        Args:
            **kwargs: Filter arguments.

        Returns:
            QuerySet: A QuerySet of matching model instances, or None if an exception occurs.
        """
        try:
            return self.access_db.filter(**kwargs)
        except:
            pass