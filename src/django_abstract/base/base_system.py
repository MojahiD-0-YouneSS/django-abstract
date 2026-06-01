from abc import ABC, abstractmethod
from django_abstract.utilities import Entry
from django_abstract.registry import get_operator

class BaseSystem(ABC):
    """Orchestration Layer for Pure Logic / External APIs.
    Coordinates multiple BaseServices. Does NOT require database transactions.

    The Pure Logic Orchestrator. Speaks 'Entry'.
    Extracts sessions, manages context, and delegates to Operators via the Registry.
    Does NOT wrap execution in a database transaction.

    Attributes:
        ALLOWED_OPERATORS (list): Whitelist of operators this system is allowed to invoke.
        SYSTEM_SLUG (str): Unique identifier for the system.
        request: The HTTP request object (if applicable).
        session_key (str): The session identifier.
        allowed_operators (list): Instance copy of ALLOWED_OPERATORS.
        system_slug (str): Instance copy of SYSTEM_SLUG.
        entry (Entry): The context entry managing state and errors.
    """

    # Whitelist: Which operators is this system allowed to invoke?
    ALLOWED_OPERATORS = []
    SYSTEM_SLUG = "base_system"

    def __init__(self, request=None, session_key=None, entry=None):
        """Initialize the BaseSystem.

        Args:
            request (HttpRequest, optional): The HTTP request object. Defaults to None.
            session_key (str, optional): The session identifier. Defaults to None.
            entry (Entry, optional): An existing Entry context. Defaults to None.
        """
        self.request = request
        self.session_key = session_key
        self.allowed_operators = self.ALLOWED_OPERATORS
        self.system_slug = self.SYSTEM_SLUG
        self.entry:Entry = entry or Entry(session_key=self.session_key, request=self.request)

    @abstractmethod
    def execute(self, *args, **kwargs):
        """The main entry point for the system.

        Must be implemented by subclasses to define the orchestration logic.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            NotImplementedError: If not implemented in the subclass.
        """
        raise NotImplementedError()

    def invoke_operator(
        self,
        operator_name: str,
        target_service: str,
        target_method: str,
        payload: dict = None,
    ):
        """Dynamically fetches an operator from the registry, validates permissions, and asks it to dispatch the action.

        Args:
            operator_name (str): The name of the operator to invoke.
            target_service (str): The target service for the operator.
            target_method (str): The target method on the service.
            payload (dict, optional): The data payload to pass. Defaults to None.

        Returns:
            bool: True if dispatched successfully, False if blocked or operator not found.
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
