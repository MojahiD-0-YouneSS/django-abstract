from django_abstract.utilities import ClassInfoProvider
from django_abstract.base.base_exception import CoreException

class UtilityException(CoreException):
    """Exception raised for errors occurring within utility functions."""
    def __init__(
        self,
        message: str = "A utility error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class LoggingException(CoreException):
    """Exception raised for logging-related errors."""
    def __init__(
        self,
        message: str = "A logging error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class OperatorServiceException(CoreException):
    """Exception raised for operator service errors."""
    def __init__(
        self,
        message: str = "A operator service  error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class OperatorException(CoreException):
    """Exception raised for operator logic errors."""
    def __init__(
        self,
        message: str = "A creator error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class ServiceException(CoreException):
    """Exception raised for generic service errors."""
    def __init__(
        self,
        message: str = "A service error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class DependencyException(CoreException):
    """Exception raised for dependency resolution or injection errors."""
    def __init__(
        self,
        message: str = "A dependency error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class CreatorException(CoreException):
    """Exception raised for errors during model creation logic."""
    def __init__(
        self,
        message: str = "A creator error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class GenericCreatorException(CreatorException):
    """Errors for the generic selector"""
    def __init__(self, operation="unspecified", **kwargs):
        message = f"Generic selector failed during {operation}"
        self.class_info_provider = ClassInfoProvider().resolve_class_infos(obj=self)
        super().__init__(
            message=message,
            error_code="GEN_SELECTOR_FAULT",
            context={**kwargs, "selector_type": "generic"}
        )

class SelectorException(CoreException):
    """Exception raised for selector logic errors."""
    def __init__(
        self,
        message: str = "A selector error occurred",
        error_code:str=None,
        original_exception=None,
        context=None
                 ):
        super().__init__(message, error_code, original_exception, context)

class GenericSelectorException(SelectorException):
    """Errors for the generic selector"""
    def __init__(self, operation="unspecified", **kwargs):
        message = f"Generic selector failed during {operation}"
        self.class_info_provider = ClassInfoProvider().resolve_class_infos(obj=self)
        super().__init__(
            message=message,
            error_code="GEN_SELECTOR_FAULT",
            context={**kwargs, "selector_type": "generic"}
        )
            #logger = exception_logger(exception_data=class_info_provider.resolve_class_infos(obj=self)

class SystemException(CoreException):
    """Exception raised for high-level system orchestration errors."""
    def __init__(
        self,
        message: str = "A System error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class ModelSystemException(CoreException):
    """Exception raised for errors within BaseModelSystem implementations."""
    def __init__(
        self,
        message: str = "A System error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class ModelServiceException(CoreException):
    """Exception raised for errors within BaseModelService implementations."""
    def __init__(
        self,
        message: str = "A System error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class ModelNotBindedException(CoreException):
    """Exception raised when a required model is not bound to a service or system."""
    def __init__(
        self,
        message: str = "A System error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)


class RegistryException(CoreException):
    """Exception raised for errors within the global registry system."""
    def __init__(
        self,
        message: str = "A System error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

