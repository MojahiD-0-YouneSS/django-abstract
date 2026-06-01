# Log Utilities

## Overview
Utilities for the logging system, primarily focusing on error formatting and context extraction.

## Functions

### exception_logger(exception_data, **kwargs)
Formats and structures an exception payload for insertion into `SystemErrorLog`.

- **Parameters**:
  - `exception_data`: Output from `ClassInfoProvider`.
  - `kwargs`: Additional context from the exception.
- **Returns**: A structured dictionary ready for the logging service.
