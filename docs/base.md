# Django-Abstract Core Architecture

django-abstract enforces Domain-Driven Design (DDD) by strictly separating concerns. Instead of writing monolithic Django views, you compose your application using our specialized base classes.

1. Data Layer (BaseModel & BaseForm)

BaseModel

An abstract Django model that provides enterprise-grade defaults to every table in your database.

UUID Primary Keys: Uses secure uuid4 instead of predictable auto-incrementing integers.

Audit Trails: Automatically tracks created_at, updated_at, created_by, and updated_by.

Soft Deletes: Built-in soft_delete() and reactivate() methods. It toggles is_active and logs deactivated_at instead of destroying data.

BaseForm

A smart ModelForm that automatically formats itself for modern frontend frameworks (like Bootstrap 5).

Auto-Styling: Injects form-control into standard inputs and form-check-input into checkboxes/radios automatically.

Audit Protection: Automatically strips out sensitive audit fields (created_by, deactivated_at) so users can't overwrite them via POST requests.

2. Dependency Injection (BaseDependency)

Instead of tightly coupling models to services, we use Dependencies.

A BaseDependency acts as a bucket for Selectors (read queries) and Creators (write queries).

Dynamic Resolution: Thanks to a custom __getattr__ implementation, accessing dependency.select_user() automatically routes to the correct localized or global registry.

3. Business Logic (BaseOperatorService & BaseModelService)

This is the brain of your application. Views do not contain logic; Services do.

BaseOperatorService: The heavyweight base class. It handles data validation via the nested BaseServiceValidator, tracks db_record states, and safely routes read_entry, create_entry, and delete_entry operations.

BaseModelService: Inherits from BaseOperatorService but adds model-specific utilities, like get_or_raise(), which standardizes 404/Missing error handling.

4. Security & Routing (BaseOperator)

Operators act as the "Bouncer" and "Router" before a Service is executed.

Uses a ControlEntryData envelope to track state.

The Bouncer (can_run): Validates if the current session or user is allowed to execute the requested target service.

The Router (run): Finds the target service in the SERVICE_REGISTRY, packs the payload, and fires the service hook safely.

5. Orchestration (BaseModelSystem)

When an action requires multiple services to run (e.g., "Checkout" requires the Order Service, Inventory Service, and Email Service), you use a System.

Transactional Safety: The run() method is permanently wrapped in transaction.atomic(). If any service fails, the entire database state rolls back safely.

Operator Invocation: Dynamically loads allowed Operators to handle the complex multi-step flows.

6. Error Handling (CoreException)

Generic 500 errors are a nightmare to debug. CoreException provides:

Standardized formatting with UTC timestamps.

Explicit error_code injection.

A context dictionary to log exactly what payload caused the failure.