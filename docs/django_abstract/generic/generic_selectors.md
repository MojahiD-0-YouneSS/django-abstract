# GenericSelector

## Overview
`GenericSelector` provides reusable filtering logic for standard attributes found across many models (like `created_at`, `is_active`, `id`, etc.).

## Attributes
- `model`: The resolved Django model class.
- `model_str_rep`: The string representation of the model class.

## Methods
- `ids(is_list=False, value=None)`: Retrieves specific IDs or a flat list of all IDs.
- `created_at(date_value)`: Filters records by creation date.
- `updated_at(date_value)`: Filters records by update date.
- `deactivated_at(date_value)`: Filters records by deactivation date.
- `deactivated_by(date_value)`: Filters records by deactivating user.
- `is_active(active=True)`: Filters records by active status.
- `is_disabled(disabled=True)`: Filters records by disabled status.
- `created_by(is_list=False)`: Retrieves creators.
- `updated_by(is_list=False)`: Retrieves updaters.

## Usage Example
```python
from django_abstract.generic.generic_selectors import GenericSelector
from myapp.models import Article

selector = GenericSelector(model_rep=Article)
active_articles = selector.is_active(True)
```
