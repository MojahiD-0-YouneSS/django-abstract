# BaseForm

## Overview
`BaseForm` extends Django's `ModelForm` to automatically exclude audit fields (like `created_at`, `updated_at`, etc.) and apply standard CSS classes (e.g., Bootstrap's `form-control`) to widgets.

## Attributes
- `deafault_exclude_fields`: List of standard audit fields to exclude automatically.
- `exclude_fields`: Dynamically populated list of fields to exclude.

## Methods
- `exclude(*fields)`: Dynamically adds fields to the exclusion list and re-processes the form.
- `_form_process()`: Internal method that applies CSS classes and removes excluded fields from the form.

## Usage Example
```python
from django_abstract.base.base_form import BaseForm
from .models import Product

class ProductForm(BaseForm):
    class Meta:
        model = Product
        fields = "__all__"

# In a view:
form = ProductForm()
form.exclude("internal_code", "supplier_price")
```
