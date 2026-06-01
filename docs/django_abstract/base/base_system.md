# BaseSystem

## Overview
`BaseSystem` acts as the primary Orchestration Layer for actions that DO NOT require strict database transactions. It defines the workflow entry point and manages the master `Entry` object.

## Attributes
- `allowed_operators`: Whitelist of operators this system is allowed to invoke.
- `request`: The incoming HTTP request.
- `session_key`: The active session identifier.
- `entry`: The master `Entry` object that holds `ControlEntryData`, `ServiceEntryData`, and `EntryData`.

## Methods
- `execute(*args, **kwargs)`: Abstract method. Must be implemented to define the main orchestration logic.
- `run(*args, **kwargs)`: Standard execution wrapper. Calls `execute()` and handles high-level failure logging.
- `invoke_operator(operator_name, target_service, target_method, payload)`: Dynamically fetches the specified operator, validates system permissions, and dispatches the payload to the service.

## Usage Example
```python
from django_abstract.base.base_system import BaseSystem

class AnalyticsSystem(BaseSystem):
    allowed_operators = ["metrics_operator"]
    
    def execute(self, path):
        self.invoke_operator("metrics_operator", "session_metrics", "record_hit", {"path": path})
```
