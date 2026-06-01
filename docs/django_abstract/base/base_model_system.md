# BaseModelSystem

## Overview
`BaseModelSystem` is identical in structure to `BaseSystem`, but **always wraps execution in a database transaction** (`transaction.atomic()`). If any service or operator fails during `.execute()`, the entire database state rolls back.

## Key Differences
- The `.run()` method enforces `transaction.atomic()`. Use this system whenever orchestrating data writes across multiple tables (e.g., fulfilling an order and updating inventory).

## Usage Example
```python
from django_abstract.base.base_model_system import BaseModelSystem

class CheckoutSystem(BaseModelSystem):
    allowed_operators = ["cart_operator", "inventory_operator"]
    
    def execute(self, cart_id):
        # If inventory update fails, the cart charge is rolled back automatically
        self.invoke_operator("cart_operator", "payment_service", "charge", {"cart_id": cart_id})
        self.invoke_operator("inventory_operator", "inventory_service", "deduct", {"cart_id": cart_id})
```
