# BaseCreator

## Overview
`BaseCreator` handles the write operations (Create, Update, Delete) for a specific Django model. It abstracts away direct database mutations, ensuring consistent data handling. Inherits from `GenericCreator`.

## Attributes
- `model_class`: The Django model to mutate.
- `status`: Execution status flag.
- `system_infos`: Resolved class information for logging/metadata.

## Methods
- `access_db`: Property returning the model's default manager (`objects`).

## Usage Example
```python
from django_abstract.base.base_creator import BaseCreator
from .models import Product

class ProductCreator(BaseCreator):
    def __init__(self):
        super().__init__(Product)
        
    def bulk_create_products(self, data_list):
        return self.access_db.bulk_create([self.model_class(**data) for data in data_list])
```
