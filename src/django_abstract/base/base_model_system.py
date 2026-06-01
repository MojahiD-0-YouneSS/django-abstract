from django.db import transaction
from abc import ABC, abstractmethod
import logging
from django_abstract.utilities import Entry
from django_abstract.registry import OPERATOR_REGISTRY

logger = logging.getLogger(__name__)


class BaseModelSystem(ABC):
    """Orchestration Layer for Database State Changes.
    
    Coordinates multiple BaseModelServices and always wraps execution in a database
    transaction to ensure atomicity.

    Attributes:
        allowed_operators (list): Whitelist of operators this system is allowed to invoke.
        request: The HTTP request object.
        session_key (str): The session identifier.
        entry (Entry): The context entry managing state.
    """

   
    allowed_operators = []

    def __init__(self, request=None, session_key=None, entry=None):
        """Initialize the BaseModelSystem.

        Args:
            request (HttpRequest, optional): The HTTP request object. Defaults to None.
            session_key (str, optional): The session identifier. Defaults to None.
            entry (Entry, optional): An existing Entry context. Defaults to None.
        """
        self.request = request
        self.session_key = session_key

        self.entry = entry or Entry(session_key=self.session_key)

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        The main entry point for the system.
        Must be implemented by subclasses.
        """
        pass

    def run(self, *args, **kwargs):
        """Standardized execution wrapper that enforces transactional integrity.

        If any execution inside `.execute()` fails, the entire database state rolls back.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The result of the `.execute()` method.
            
        Raises:
            Exception: Re-raises the exception after handling failure.
        """
        try:
            with transaction.atomic():
                return self.execute(*args, **kwargs)
        except Exception as e:
            self.handle_failure(e)
            raise  # Re-raise to ensure the caller knows it failed
   
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
        OperatorClass = OPERATOR_REGISTRY.get(operator_name)
        if not OperatorClass:
            self.entry.errors["system"] = (
                f"Operator '{operator_name}' not found in OPERATOR_REGISTRY."
            )
            return False

        # 3. Instantiate the Operator (Passing the Master Entry)
        # The Operator will internally focus on the ControlEntryData
        operator_instance = OperatorClass(entry=self.entry)

        # 4. Dispatch!
        return operator_instance.dispatch(
            target_service_name=target_service,
            target_method=target_method,
            payload=payload,
        )
