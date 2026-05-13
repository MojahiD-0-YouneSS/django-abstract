from abc import ABC
from django_abstract.registry import SERVICE_REGISTRY
from django_abstract.utilities import  ControlEntryData, ControlDataOperator, to_snake_case, ServiceEntryData

class BaseAbstractOperator(ABC):
    """
    All guest operators must inherit this class.
    """
    def __init__(self, session_key=None,domain=None):
        self.session_key = session_key
        self.domain=domain
    def run(self):
        """
        Default run method. Should be overridden.
        """
        raise NotImplementedError

    def can_run(self):
        """
        Optional hook for conditional execution, e.g., time-sensitive or based on data.
        """
        raise NotImplementedError

class BaseOperator(BaseAbstractOperator):
    """
    All guest operators must inherit this class.
    """
    allowed_services = []
    def __init__(self, session_key=None, domain=None):
        self.entry = ControlEntryData(operator=to_snake_case(self.__class__.__name__))
        self.entry_operator = ControlDataOperator(self.entry)
        super().__init__(session_key=session_key,domain=domain)

    def can_run(self, target_service_name: str) -> bool:
        """
        The Bouncer Logic: Override this in subclasses (like SessionOperator)
        to check tokens, session flags, or guest status.
        """
        if target_service_name not in self.allowed_services:
            self.entry.service_entry_data.errors["operator_auth"] = (
                f"Operator blocked access to {target_service_name}."
            )
            return False

        # Example: Check if a global kill-switch was thrown in the control flags
        if self.entry.control_operator.has_flag("is_disabled"):
            self.entry.service_entry_data.errors["operator_auth"] = (
                "This flow is currently disabled."
            )
            return False

        return True

    def run(
        self, target_service_name: str, target_method: str, payload: dict = None
    ):
        """
        The Router Logic: Finds the service, packs the payload, and fires.
        """
        if not self.can_run(target_service_name):
            return False

        # 1. Prepare the standard envelope payload
        payload = payload or {}
        entry = ServiceEntryData(model_name=None)
        entry.service_data.update(payload)
        entry.service_data["method_name"] = target_method

        # 2. Find Target in Registry (It doesn't matter which type it is!)
        target_class = SERVICE_REGISTRY.get("MODEL_SERVICE", {}).get(
            target_service_name
        )
        if not target_class:
            # Fallback to pure logic services
            target_class = SERVICE_REGISTRY.get("BARE_SERVICE", {}).get(
                target_service_name
            )

        # 3. Fire!
        if target_class:
            # Instantiate the service
            service_instance = target_class(session_key=self.session_key)

            # Pass the fully populated payload directly into the service's hook
            success = service_instance.hook(entry=entry.service_entry_data)
            return success

        self.entry.flags["operator"] = (
            f"Service '{target_service_name}' not found."
        )
        return False
