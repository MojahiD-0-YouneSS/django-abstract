from django_abstract.base.base_operator_service import BaseOperatorService
from django_abstract.exceptions import ModelServiceException

class BaseModelService(BaseOperatorService):
    """
    Model-Specific Logic Layer.
    Inherits from BaseOperatorService, meaning it automatically has access
    to self.selector and self.creator for the registered model.
    """
    service_slug = None
    # You can add generic utility methods here that apply to ALL models,
    # for example, a standardized "soft delete" method if your models support it.

    def get_or_raise(self, **kwargs):
        """Standardized fetch with strict error handling."""
        instance = self.selector.get(**kwargs)
        if not instance:
            raise ModelServiceException(
                f"{self.model_class.__name__} not found with parameters: {kwargs}"
            )
        return instance
