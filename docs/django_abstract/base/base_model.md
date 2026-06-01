# BaseModel

## Overview
`BaseModel` provides a foundational Django model abstraction that adds standard audit fields and implements generic soft-deletion mechanics out of the box.

## Fields
- `id`: UUIDField (Primary Key).
- `created_at`: DateTimeField (auto-populated on creation).
- `updated_at`: DateTimeField (auto-updated on save).
- `is_active`: BooleanField (defaults to True).
- `is_disabled`: BooleanField (defaults to False).
- `deactivated_at`: DateTimeField.
- `deactivated_by`: CharField.
- `created_by`: CharField.
- `updated_by`: CharField.
- `notes`: TextField.

## Methods
- `deactivate(user_id=None)`: Soft-deletes the record by setting `is_active=False` and recording the timestamp/user.
- `activate()`: Re-activates a soft-deleted record.
- `disable()`: Marks the record as completely disabled (distinct from soft-delete).

## Usage Example
```python
from django_abstract.base.base_model import BaseModel
from django.db import models

class Product(BaseModel):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
```
