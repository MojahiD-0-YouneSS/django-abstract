from abc import ABC, abstractmethod
from django_abstract.utilities import Entry
from django_abstract.registry import get_operator

class BaseSystem(ABC):
    """
    Orchestration Layer for Pure Logic / External APIs.
    Coordinates multiple BaseServices. Does NOT require database transactions.
    """

    """
    The Pure Logic Orchestrator. Speaks 'Entry'.
    Extracts sessions, manages context, and delegates to Operators via the Registry.
    Does NOT wrap execution in a database transaction.
    """

    # Whitelist: Which operators is this system allowed to invoke?
    ALLOWED_OPERATORS = []
    SYSTEM_SLUG = "base_system"

    def __init__(self, request=None, session_key=None, entry=None):
        self.request = request
        self.session_key = session_key
        self.allowed_operators = self.ALLOWED_OPERATORS
        self.system_slug = self.SYSTEM_SLUG
        self.entry:Entry = entry or Entry(session_key=self.session_key, request=self.request)

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        The main entry point for the system.
        Must be implemented by subclasses.
        """
        raise NotImplementedError()

    def invoke_operator(
        self,
        operator_name: str,
        target_service: str,
        target_method: str,
        payload: dict = None,
    ):
        """
        Dynamically fetches an operator from the registry, validates permissions,
        and asks it to dispatch the action.
        """
        # 1. System-level whitelist validation
        if operator_name not in self.allowed_operators:
            self.entry.errors["system"] = (
                f"System blocked: Cannot invoke operator '{operator_name}'."
            )

            return False

        # 2. Fetch from Registry
        OperatorClass = get_operator(operator_name)
        if not OperatorClass:
            self.entry.service_entry_data.errors["system"] = (
                f"Operator '{operator_name}' not found in OPERATOR_REGISTRY."
            )
            return False

        # 3. Instantiate the Operator (Passing the Master Entry)
        # The Operator will internally focus on the ControlEntryData

        operator_instance = OperatorClass(entry=self.entry.control_entry_data)
        # 4. Dispatch!
        return operator_instance.run(
            target_service_name=target_service,
            target_method=target_method,
            payload=payload,
        )
