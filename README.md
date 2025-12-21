#🏗️ Django Abstract

Django Abstract provides the missing architectural layers for complex Django applications. It moves beyond the standard Model-View-Template (MVT) pattern by introducing Creators (Write Logic), Selectors (Read Logic), and Base Abstractions to keep your codebase clean, testable, and scalable.

#⚡ Why Use This?

Standard Django is great, but "Fat Models" and "Fat Views" become unmaintainable in large projects. django-abstract solves this by enforcing separation of concerns:

🧱 **Base Models**: Pre-configured UUIDs, timestamps, and soft-delete logic.

⚙️ **Creator Layer**: A standardized way to handle business logic (Writes), decoupling it from Views/APIs.

🔍 **Selector Layer**: Optimized query logic (Reads) that prevents N+1 issues and leaking logic into templates.

💉 **Dependency Injection**: A registry system (@creator_selector) to wire domains together without circular imports.

#📦 Installation
```bash
pip install django-abstract
```

#🚀 Core Architecture

**1. The Base Model**

Stop repeating created_at and updated_at.
```python
from django_abstract.core.base_model import BaseModel

class Product(BaseModel):
    # Automatically gets:
    # - id (UUID)
    # - created_at / updated_at
    # - is_active / is_deleted (Soft Delete)
    name = models.CharField(max_length=255)
```

**2. The Creator Layer (Writer)**

Encapsulate your data creation logic. creator take model class not raw requests or via decorator.
```python
from django_abstract.core.service import BaseCreator, CreatorException
from .models import Order

class OrderCreator(BaseService):
    def __init__(self,*args,**kwargs):
        super().__init__(Order)
    def execute(self, user_status):
        # 1. Validate Business Rules
        if user_status == 'banned':
            raise CreatorException("User banned") # CreatorException: unabel to create this entry . reason: User banned

        # 2. Perform Atomic Transaction
        with transaction.atomic():
            order = self.model_class.objects.create(...)
            # ... update inventory ...
        return order
```

3. **The Selector Layer (Reads)**

Keep your queries optimal and reusable.
```python
from django_abstract.core.selector import BaseSelector
from .models import Product

class ProductSelector(BaseSelector):
    def __init__(self,):
        super().__init__(Product)
    def get_active_products(self,):
        return self.model_class.objects.filter(is_active=True).select_related('category')
````

4. **The Registry Pattern**

Automatically wire up your domains using the dependency registry.
```python
from django_abstract.core.registry import creator_selector
from .dependencies import CartDependency

@creator_selector(dependency=CartDependency) # -> makes a regestry of selector/creator classes but only if same structure
class Cart(BaseModel):
    # This model is now auto-registered with the Cart Domain
    pass
# were CartDependency
'''
from django_abstract.core.base_dependency import BaseDependency
from dataclasses import dataclass

@dataclass
class CartDependency(BaseDependency):
    """
    CartAppDependency is a dataclass that serves as a container for the cart app's dependencies.
    It inherits from BaseDependency, which provides a base structure for defining dependencies in the application.
    """
    name: str = "cart"
    description: str = "Cart app dependency"
```
🛠️ **The "Guest Mode" Ecosystem**

django-abstract includes a specialized system for handling unauthenticated user state (e.g., Guest Carts).

Operators: Atomic command classes that oversees each app or sub apps (CartOperator (has all cart actioins), ProductOperator).

Dispatcher: Routes requests based on user state (Anon vs. Auth).

Middleware: Manages persistent guest sessions via cookies.


📜 License MIT License - Copyright (c) 2025 Youness Mojahid
