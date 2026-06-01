<div align="center">
  <h1>🛡️ Django Abstract</h1>
  <p><strong>An Enterprise-Grade Architectural Layer for Django</strong></p>
  <p>Clean Architecture | Dependency Injection | CQRS Principles | Domain-Driven Design</p>
</div>

---

## 📖 Overview

**Django Abstract** is a highly advanced framework built on top of Django that strictly enforces **Clean Architecture** and **Domain-Driven Design (DDD)**. It solves the infamous "Fat Model / Fat View" anti-pattern by completely decoupling:

1. **Data Access** (`Selectors` / `Creators`)
2. **Business Logic** (`Services`)
3. **Flow Control & Permissions** (`Operators` / `Systems`)

This framework provides a unified, predictable way to scale complex Django applications, manage high-throughput operations via Redis queues, and dynamically inject dependencies.

## 🚀 Key Features

### 🧩 Global Registry & Dependency Injection
- Dynamically registers all architectural components using decorators (`@creator_selector`, `@register_service`, `@register_operator`).
- Injects `BaseDependency` instances at runtime to prevent circular imports and allow test mocking.
- Magic attribute resolution (`__getattr__`) allows developers to resolve dependencies seamlessly (`dependency.select_user`).

### 🏛️ Strict Architectural Separation
- **`BaseModel`**: Adds soft-delete, active toggles, and rich audit trails natively.
- **`BaseSelector` / `BaseCreator`**: Isolates raw Django ORM calls from business logic.
- **`BaseService`**: Pure business logic that operates exclusively on an abstract `ServiceEntryData` state.
- **`BaseSystem`**: Orchestrates workflows and manages global database transactions (`transaction.atomic()`).

### ⚡ High-Throughput Background Logging
- Includes a robust `log/` app that tracks `SystemErrorLog`, `SessionMetrics`, and `AdminActionLog`.
- Uses a **Redis-backed queueing system** within `ModelServices` to buffer high-frequency inserts and bulk-flush (`bulk_create`) them to PostgreSQL, completely preventing database locking during traffic spikes.

### 🔌 Seamless View Binding
- Replaces traditional Django Views with `EntryBindingMixin`.
- Automatically extracts `session_key`, `ip_address`, and POST/GET payloads, hydrates a master `Entry` object, and passes it directly to the orchestration `Systems`.

## 📁 Repository Structure

```text
src/django_abstract/
├── base/        # Core architectural base classes
├── generic/     # Generic, reusable creation/selection patterns
├── log/         # High-performance asynchronous auditing system
├── registry.py  # Global Dependency Injection container
└── utilities.py # Context extraction, View Mixins, State Objects
```

## 📚 Documentation
Comprehensive documentation for every module can be found in the `docs/` folder:
- [Base Architecture Overview](docs/django_abstract/base)
- [Generic Utilities](docs/django_abstract/generic)
- [High-Performance Logging](docs/django_abstract/log)

## 🧪 Testing
The repository is fully testable. Due to strict dependency injection, any `Selector` or `Creator` can be swapped out with a mock class during tests. Test stubs for all modules are located in the `tests/` directory.

## 👨‍💻 Author
Designed and implemented as an enterprise architectural study to showcase advanced systems design, Python metaprogramming, and scalable Django architecture.
