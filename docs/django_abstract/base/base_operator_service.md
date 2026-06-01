# BaseOperatorService

## Overview
`BaseOperatorService` is the core service base class that bridges `BaseService` logic with Django model dependencies. It manages validation, caching bulk updates, and database transaction tracking.

## Attributes
- `model_dependency`: The injected model dependency registry.
- `model_slug`: The slug identifying the target model.
- `last_updated`: Timestamp of the last bulk update.
- `operator_class`: Set to `ServiceDataOperator`.
- `entry_class`: Set to `ServiceEntryData`.

## Key Features
- **Validation**: Implements an inner `BaseServiceValidator` class to handle `MINIMUM_WRITE_FIELDS` and permission checks before any method runs.
- **Bulk Updating**: Collects pending updates in memory and only flushes to the database via `bulk_update` periodically (e.g., every 5 seconds) to prevent database locking on high-throughput models.
- **Auto-loading**: Automatically loads the target database record into memory upon instantiation if `load_record=True`.

## Usage Example
Usually, developers inherit from `BaseModelService` instead of directly from `BaseOperatorService`, but it can be used for custom logic bridging.
