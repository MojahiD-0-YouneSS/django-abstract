from django_abstract.base.base_operator_service import BaseOperatorService
from django_abstract.exceptions import ModelServiceException

class BaseModelService(BaseOperatorService):
    """Model-Specific Logic Layer.
    
    Inherits from BaseOperatorService to provide direct access to selectors and creators
    for a registered Django model.

    Attributes:
        service_slug (str, optional): Unique slug identifying the service.
    """
    service_slug = None
    # You can add generic utility methods here that apply to ALL models,
    # for example, a standardized "soft delete" method if your models support it.

    def get_or_raise(self, **kwargs):
        """Standardized fetch operation with strict error handling.

        Args:
            **kwargs: Query parameters for the selector.

        Returns:
            Model: The retrieved database instance.

        Raises:
            ModelServiceException: If the instance is not found.
        """
        instance = self.selector.get(**kwargs)
        if not instance:
            raise ModelServiceException(
                f"{self.model_class.__name__} not found with parameters: {kwargs}"
            )
        return instance
