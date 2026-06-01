# BaseSelector

## Overview
`BaseSelector` acts as the read-only layer of the data access pattern. It abstracts away complex Django ORM queries into clean, testable methods.

## Attributes
- `model_class`: The Django model this selector is responsible for.

## Methods
- `__init__(model_class)`: Initializes the selector.
- `get(**kwargs)`: Returns a single instance matching the query parameters or None.
- `filter(**kwargs)`: Returns a queryset of instances matching the query parameters.
- `all()`: Returns all instances of the model.
- `exists(**kwargs)`: Checks if any instances match the parameters.
- `count(**kwargs)`: Returns the count of matching instances.

## Usage Example
```python
from django_abstract.base.base_selector import BaseSelector
from .models import Product

class ProductSelector(BaseSelector):
    def __init__(self):
        super().__init__(Product)
        
    def get_expensive_products(self):
        return self.filter(price__gt=1000)
```
