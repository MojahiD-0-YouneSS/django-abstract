# BaseDependency

## Overview
`BaseDependency` is the foundation for dependency injection in the framework. It acts as a registry container, allowing components (like selectors and creators) to be resolved dynamically via custom `__getattr__` logic.

## Attributes
- `_registry`: The global or domain-specific registry (usually `GLOBAL_REGISTRY`).
- `selectors`: A mapping of registered selectors for this dependency.
- `creators`: A mapping of registered creators for this dependency.
- `model_class`: The associated Django model class, automatically attached during registration.

## Dynamic Resolution
The magic of `BaseDependency` comes from overriding `__getattr__`. 
- If you call `dependency.select_user`, it checks `selectors` in the registry and instantiates the `UserSelector`.
- If you call `dependency.create_user`, it checks `creators` and instantiates the `UserCreator`.

## Usage Example
```python
from django_abstract.base.base_dependency import BaseDependency
from django_abstract.registry import creator_selector

class ShopDependency(BaseDependency):
    app_name = "shop"
    domain = "e-commerce"

@creator_selector(dependency=ShopDependency())
class Product(BaseModel):
    name = models.CharField(max_length=255)

# Later in the code:
dependency = ShopDependency()
selector = dependency.select_product # Returns ProductSelector instance
```
