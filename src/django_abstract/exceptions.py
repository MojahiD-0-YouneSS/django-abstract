from django_abstract.selectors_exceptions import SelectorException
from django_abstract.utilities import ClassInfoProvider
from django_abstract.base_exception import CoreException
from django_abstract.selectors_exceptions import CreatorException

class UtilityException(CoreException):
    def __init__(
        self,
        message: str = "A utility error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class LoggingException(CoreException):
    def __init__(
        self,
        message: str = "A logging error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class OperatorServiceException(CoreException):
    def __init__(
        self,
        message: str = "A operator service  error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class OperatorException(CoreException):
    def __init__(
        self,
        message: str = "A creator error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class ServiceException(CoreException):
    def __init__(
        self,
        message: str = "A service error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class DependencyException(CoreException):
    def __init__(
        self,
        message: str = "A dependency error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)

class CreatorException(CoreException):
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
    def __init__(
        self,
        message: str = "A System error occurred",
        error_code= None,
        original_exception = None,
        context = None
    ):
        super().__init__(message, error_code, original_exception,  context)
