# BaseService

## Overview
`BaseService` is the pure business logic layer. It operates entirely on `ServiceEntryData` and does NOT have direct database dependencies (unlike `BaseModelService`). 

## Key Concepts
- **Validation**: Enforces `MINIMUM_WRITE_FIELDS` or required payload parameters before execution.
- **State Mutation**: Operations update `self.entry.service_data` instead of returning discrete values, ensuring a uniform data pipeline.
- **Hook Architecture**: Uses hooks and execution proxies to chain multiple services together cleanly.

## Attributes
- `operator_class`: Set to `ServiceDataOperator`.
- `entry_class`: Set to `ServiceEntryData`.
- `hooks_list`: Allowed hooks.

## Methods
- `init_state_hook()`: Initializes the entry and operator state.
- `hook()`: Lifecycle execution method to be called by operators.

## Usage Example
```python
from django_abstract.base.base_service import BaseService
from django_abstract.registry import register_service, action_method_fields

@register_service(service_type="BARE_SERVICE")
class EmailNotificationService(BaseService):
    
    @action_method_fields("email_address", "template_id")
    def send_welcome_email(self, email_address, template_id):
        # Call third party API
        self.entry.service_data.update({"email_sent": True})
        return self.entry
```
