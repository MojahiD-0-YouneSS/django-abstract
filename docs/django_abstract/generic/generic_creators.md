# GenericCreator

## Overview
`GenericCreator` provides reusable creation logic for common Django model attributes. Rather than writing `.create()` methods for every field manually, `GenericCreator` centralizes the logic.

## Attributes
- `model`: The resolved Django model class.
- `model_rep`: The string representation of the model class.
- `creator_info`: Resolved metadata about the creator class.

## Methods
- `deactivated_by(name, is_get_or_create=False)`: Creates or gets a record based on the user who deactivated it.
- `created_by(name, is_get_or_create=False)`: Creates or gets a record based on the creator.
- `updated_by(name, is_get_or_create=False)`: Creates or gets a record based on the updater.

## Usage Example
```python
from django_abstract.generic.generic_creators import GenericCreator

creator = GenericCreator(model_rep="auth.User", is_model=False)
creator.created_by(name="admin", is_get_or_create=True)
```
