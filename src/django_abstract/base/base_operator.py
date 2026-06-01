from abc import ABC
from django_abstract.registry import get_service,SERVICE_REGISTRY
from django_abstract.utilities import  ControlEntryData, ControlDataOperator, to_snake_case, ServiceEntryData
from typing import Any

class BaseAbstractOperator(ABC):
    """Abstract base class for all operators.
    
    Operators define the rules for who can access what services and under what conditions.

    Attributes:
        session_key (str, optional): The current session identifier.
        domain (str, optional): The domain the operator belongs to.
    """
    def __init__(self, session_key=None,domain=None):
        """Initialize the BaseAbstractOperator.

        Args:
            session_key (str, optional): The session identifier.
            domain (str, optional): The operator domain.
        """
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
    """Concrete base class for operator implementations.

    Attributes:
        allowed_services (list): Whitelist of service names this operator can invoke.
        domain (str, optional): The domain context for the operator.
        entry (ControlEntryData): The entry data tracking state and errors.
        entry_operator (ControlDataOperator): The operator to mutate the entry data.
    """
    allowed_services = []
    domain=None
    def __init__(self, session_key=None, domain=None,entry=None):
        """Initialize the BaseOperator.

        Args:
            session_key (str, optional): The session identifier.
            domain (str, optional): The domain context.
            entry (ControlEntryData, optional): The state tracking entry.
        """
        self.entry = entry or ControlEntryData(
            operator=to_snake_case(self.__class__.__name__)
        )
        self.entry_operator = ControlDataOperator(self.entry)
        super().__init__(session_key=session_key,domain=domain)
        if not self.entry.operator:
            self.entry.operator = to_snake_case(self.__class__.__name__)
        self.validator = self.BaseOperatorValidator

    class BaseOperatorValidator:
        def __init__(self,entry:ControlEntryData,parent_operator=None) -> None:
            self.entry=entry
            self.parent_operator=parent_operator
            self.METHOD_COLLECTION = {}
            self.meta_hook()

        def meta_hook(self,):
            raise NotImplementedError()

        def register_method(self,method_name,method):
            self.METHOD_COLLECTION[method_name]=method

        def get_validation_method(self,):
            return self.METHOD_COLLECTION.values()

    def can_run(self, target_service_name: str) -> bool:
        """
        The Bouncer Logic: Override this in subclasses (like SessionOperator)
        to check tokens, session flags, or guest status.
        """
        if target_service_name not in self.allowed_services:
            self.entry.errors["operator_auth"] = (
                f"Operator blocked access to {target_service_name}."
            )
            return False

        # Example: Check if a global kill-switch was thrown in the control flags
        if self.entry_operator.has_flag("is_disabled"):
            self.entry.flags["errors"][
                self.entry_operator.entry.operator
            ] = "This flow is currently disabled."
            return False

        try:
            validator = self.validator(self.entry,self)
            for method in validator.get_validation_method():
                method()
            return True
        except Exception as e:
            # raise e
            return False

    def run(
        self,
        payload: dict[str,Any],
        target_service_name: str | None = None,
        target_method: str | None = None,
        target_service_args:dict|None=None
    ):
        """
        The Router Logic: Finds the service, packs the payload, and fires.
        """
        target_service_name = target_service_name or self.entry.service_name
        target_method = target_method or payload.get('method_name')
        target_service_args = target_service_args or self.entry.service_args
        if not self.can_run(target_service_name):
            return False

        # 1. Prepare the standard envelope payload
        payload = payload or {}
        entry = ServiceEntryData(model_name=None)
        entry.service_data.update(payload)
        entry.service_data["method_name"] = target_method

        # 2. Find Target in Registry (It doesn't matter which type it is!)
        target_class = get_service(target_service_name)

        # 3. Fire!

        if target_class:
            # Instantiate the service

            service_instance = target_class(
                **target_service_args
            )

            # Pass the fully populated payload directly into the service's hook
            success = service_instance.hook(entry=entry)
            
            return success

        self.entry.flags["operator"] = (
            f"Service '{target_service_name}' not found."
        )
        return False
