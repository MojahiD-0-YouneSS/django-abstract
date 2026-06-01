# BaseModelService

## Overview
`BaseModelService` inherits from `BaseOperatorService` and acts as the Model-Specific Logic Layer. It automatically gains access to the `selector` and `creator` for a registered Django model.

## Attributes
- `service_slug`: Unique identifier for the service.

## Methods
- `get_or_raise(**kwargs)`: Standardized fetch operation that raises a `ModelServiceException` if the record is not found, ensuring strict data expectations.

## Usage Example
```python
from django_abstract.base.base_model_service import BaseModelService
from django_abstract.registry import register_service

@register_service()
class ProductModelService(BaseModelService):
    model_dependency = ShopDependency()
    model_slug = "product"
    
    def fetch_product(self, product_id):
        return self.get_or_raise(id=product_id)
```
