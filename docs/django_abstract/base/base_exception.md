# CoreException

## Overview
`CoreException` provides a standardized exception hierarchy for the entire framework. It allows for contextual error reporting and captures execution state, making debugging significantly easier.

## Attributes
- `message`: Human-readable error message.
- `error_code`: Specific application error code.
- `original_exception`: The underlying exception (if wrapping an existing error).
- `context`: Additional dictionary payload associated with the error.
- `timestamp`: UTC timestamp of when the exception occurred.

## Derived Exceptions
The framework defines several derived exceptions in `exceptions.py`, such as:
- `ServiceException`
- `SelectorException`
- `SystemException`
- `ModelNotBindedException`

## Usage Example
```python
from django_abstract.base.base_exception import CoreException

def do_something_risky():
    try:
        1 / 0
    except ZeroDivisionError as e:
        raise CoreException(
            message="Math calculation failed",
            error_code="MATH_001",
            original_exception=e,
            context={"user_id": 123}
        )
```
