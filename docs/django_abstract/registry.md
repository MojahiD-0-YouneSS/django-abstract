# Global Registry

## Overview
`registry.py` is the central nervous system of `django-abstract`. It uses custom decorators to automatically index and wire up all Models, Selectors, Creators, Services, Operators, and Systems across the entire codebase.

## Key Decorators

### `@creator_selector(name, dependency)`
Attached to a Django model. Automatically generates and registers a `BaseCreator` and `BaseSelector` for the model into the specified `dependency`.

### `@register_service(name, service_type)`
Registers a service class into `SERVICE_REGISTRY` (categorized as either `MODEL_SERVICE` or `BARE_SERVICE`).

### `@register_operator()`
Registers an operator class into `OPERATOR_REGISTRY`.

### `@register_system()`
Registers a system orchestration class into `SYSTEM_REGISTRY`.

## Dependency Resolution
The registry exposes global helper functions like `get_service()`, `get_operator()`, and `get_app_dependency()` to dynamically resolve instances at runtime, avoiding circular imports.
