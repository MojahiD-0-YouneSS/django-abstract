# BaseOperator

## Overview
`BaseOperator` defines the flow control and permission layer. Operators determine who can access which services under what conditions. They act as "Routers" inside the `BaseSystem` to delegate actions to specific `BaseServices`.

## Attributes
- `allowed_services`: A whitelist of service names this operator is allowed to invoke.
- `domain`: The domain context the operator belongs to.
- `entry`: A `ControlEntryData` instance tracking execution state, flags, and errors.
- `entry_operator`: A `ControlDataOperator` to mutate the entry data.

## Methods
- `dispatch(target_service_name, target_method, payload)`: Validates if the service is allowed, instantiates it with the current payload, and executes the target method.

## Usage Example
```python
from django_abstract.base.base_operator import BaseOperator
from django_abstract.registry import register_operator

@register_operator()
class GuestCartOperator(BaseOperator):
    allowed_services = ["cart_model_service", "session_metrics_service"]
    
    def dispatch(self, target_service_name, target_method, payload):
        # Additional permission checks for guests
        return super().dispatch(target_service_name, target_method, payload)
```
