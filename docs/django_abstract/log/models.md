# Log Models

## Overview
The `log` app defines essential auditing and metadata models. These models inherit from `BaseModel` to gain soft-delete capabilities and audit trails.

## Models

### FeatureToggle
Controls application behavior dynamically without deploying code.
- **Fields**: `name`, `status` (Boolean), `metadata` (JSON).

### GenericActivityLog
Records generic domain events.
- **Fields**: `name`, `description`, `domain`, `app_name`, `severity` (INFO, WARN, CRITICAL), `metadata`.

### SystemErrorLog
High-volume error logging table. Usually fed from Redis bulk-flushes.
- **Fields**: `session_key`, `endpoint`, `domain`, `method`, `error_type`, `error_message`, `trace_back`.

### AdminActionLog
Tracks sensitive admin mutations.
- **Fields**: `admin_id`, `action_type`, `target_model`, `target_id`, `changes` (JSON).
