# Framework Exceptions

## Overview
`exceptions.py` defines the global exception hierarchy used throughout the `django-abstract` framework. All exceptions inherit from `CoreException` (defined in `base_exception.py`), providing a unified error handling approach that captures tracebacks, error codes, and request context.

## Core Exception Classes
- **`UtilityException`**: Raised during failures in utility functions or generic helpers.
- **`LoggingException`**: Raised during failures in the logging infrastructure.
- **`OperatorServiceException`**: Raised when a `BaseOperatorService` encounters a structural or logical failure.
- **`OperatorException`**: Raised when flow control fails (e.g., unauthorized access).
- **`ServiceException`**: Raised within `BaseService` logic.
- **`DependencyException`**: Raised when `BaseDependency` fails to resolve a selector or creator.
- **`CreatorException` & `SelectorException`**: Raised during database read/write failures.
- **`SystemException`**: Raised during high-level orchestrator failures.
- **`RegistryException`**: Raised if an invalid class is registered in the `GLOBAL_REGISTRY`.
