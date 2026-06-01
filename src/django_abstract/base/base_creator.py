# core creators.py

from  django.db import  IntegrityError, transaction
from django_abstract.utilities import ClassInfoProvider
from django_abstract.generic.generic_creators import GenericCreator


class BaseCreator(GenericCreator):
    """Base creator class for instantiating database models.

    Attributes:
        model_class (Type[Model]): The Django model class to create instances for.
        status (bool): Status flag for the creation process.
        system_infos (dict): Resolved class information for logging/metadata.
    """
    def __init__(self, model_class):
        """Initialize the BaseCreator.

        Args:
            model_class (Type[Model]): The Django model class.
        """
        self.model_class = model_class
        self.status=False
        self.system_infos = ClassInfoProvider().resolve_class_info(obj=self)
        super().__init__(model_rep=model_class)
    @property
    def access_db(self):
        """Access the default manager of the model class.

        Returns:
            Manager: The default Django model manager (e.g., objects).
        """
        return self.model_class.objects
    