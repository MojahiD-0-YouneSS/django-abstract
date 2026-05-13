from django.db import transaction
from abc import ABC, abstractmethod
import logging
from django_abstract.utilities import Entry
from django_abstract.registry import OPERATOR_REGISTRY

logger = logging.getLogger(__name__)


class BaseModelSystem(ABC):
    """
    Orchestration Layer for Database State Changes.
    Coordinates multiple BaseModelServices.
    ALWAYS wraps execution in a database transaction to ensure atomicity.
    """

   
    allowed_operators = []

    def __init__(self, request=None, session_key=None, entry=None):
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
        """
        Standardized execution wrapper that ENFORCES transactional integrity.
        If any BaseModelService fails inside .execute(), the entire DB state rolls back.
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
