from django_abstract.utilities import (
    ClassInfoProvider,
    ServiceEntryData,
    ServiceDataOperator,
)
from django.core.exceptions import ValidationError
from django_abstract.log.utilities import ErrorSuccessLogger
from abc import ABC, abstractmethod

class BaseService(ClassInfoProvider, ABC):
    """
    Pure Business Logic Layer.
    Mimics BaseOperatorService but operates entirely in-memory using ServiceEntryData.
    """

    hooks_list = []
    entry_class = ServiceEntryData
    operator_class = ServiceDataOperator
    service_slug = None

    def __init__(self, session_key=None, **raw_data):
        self.session_key = session_key
        self.validator = self.BaseServiceValidator

        # Initialize ServiceEntryData directly (No DB load)
        self.entry = self.entry_class(raw_data=raw_data, service_data={})

        # Include operator for API consistency with ModelServices
        self.operator = self.operator_class(self.entry)
        self.operator.init_default_state()

    class BaseServiceValidator(ABC):
        def __init__(self, parent_service, **data):

            self.SERVICE_DOMAIN_FIELDS = []
            self.METHOD_COLLECTION = {}
            self.VALID_FIELDS = {}
            self.VALID_FIELDS_PER_ACTION = {}

            # Removed RESERVED_DB_METHODS since there is no DB here!

            self.parent_service = parent_service
            self.data = data
            self.cross_domain_data = {}
            self.is_cross_domain = False
            self.behavior = ServiceEntryData()
            self.meta_hook()
            self.run_service_check()

        def load_settings(self, settings):
            self.SERVICE_DOMAIN_FIELDS = settings.SERVICE_DOMAIN_FIELDS
            self.VALID_FIELDS = settings.VALID_FIELDS
            self.VALID_FIELDS_PER_ACTION = settings.VALID_FIELDS_PER_ACTION
            self.VALID_FIELDS_PER_ACTION = settings.VALID_FIELDS_PER_ACTION
            return self

        def can_run(self, *required_fields: str, dry_run=False, **data) -> bool:
            fields = (
                required_fields
                if required_fields
                else self.SERVICE_DOMAIN_FIELDS
            )
            raw_data = data if data else self.data

            if fields:
                for field in fields:
                    if field not in raw_data or raw_data[field] is None:
                        if not dry_run:
                            raise ValidationError(
                                f"Missing or invalid logic field: {field}"
                            )
                        else:
                            return False
            return True

        @abstractmethod
        def meta_hook(self):
            """Lifecycle hook: Must be overridden in subclasses to build registries."""
            pass

        def run_service_check(self, *required_fields, **data):
            raw_data = (data or self.data).copy()
            if self.is_cross_domain:
                raw_data.update(self.cross_domain_data)

            method_name = raw_data.get("method_name")
            if method_name:
                method_required_fields = self.VALID_FIELDS_PER_ACTION.get(
                    method_name, []
                )
                check = self.can_run(
                    *method_required_fields,
                    **{k: v for k, v in raw_data.items() if k != "method_name"},
                )
            else:
                check = self.can_run(*required_fields, **raw_data)

            if check:
                for field in self.SERVICE_DOMAIN_FIELDS:
                    if field in raw_data:
                        self.VALID_FIELDS[field] = raw_data[field]
                return self.VALID_FIELDS
            return {}

        def regester_method(self, name, method):
            self.METHOD_COLLECTION[name] = method
            return self

        def get_method_args(self, method_name):
            valid_fields = self.VALID_FIELDS_PER_ACTION.get(method_name, [])
            valid_domain_fields = self.run_service_check(*valid_fields)

            if self.is_cross_domain:
                return [
                    valid_domain_fields.get(field)
                    for field in self.cross_domain_data.keys()
                    if field in valid_domain_fields
                ]
            return [valid_domain_fields.get(field) for field in valid_fields]

        def run(self, method_name):
            if not method_name or not self.METHOD_COLLECTION:
                return False

            method = self.METHOD_COLLECTION.get(method_name)
            if method:
                method()
                return True
            return False

    def can_run(self, method_name, **kwargs) -> bool:
        kwargs["method_name"] = method_name
        validator = self.validator(self, **kwargs)
        required_fields = validator.VALID_FIELDS_PER_ACTION.get(method_name, [])
        flag = validator.can_run(*required_fields)
        if flag:
            self.entry.service_data = validator.behavior.service_data
        return flag

    def run(self, method_name, **kwargs):
        """
        Main execution wrapper for pure logic services.
        """
        kwargs["method_name"] = method_name
        validator = self.validator(self, **kwargs)

        success = validator.run(method_name=method_name)
        if success:
            # Transfer computed result back to the main service state
            self.entry.service_data.update(validator.behavior.service_data)

        return success

    def hook(self, entry: ServiceEntryData = None):
        """Allows this logic service to be triggered by other services."""
        entry = entry or self.entry
        service_data = entry.service_data.copy()

        # Automatically pull method_name if passed via service_data
        method_name = service_data.get("method_name")

        if method_name and self.can_run(**service_data):
            return self.run(**service_data)
        return None

    def hook_pad(
        self, *hook_names: str, entry: ServiceEntryData = None, service_type: str = None
    ):
        """Passes the ServiceEntryData along to Model Services or other Pure Services"""
        service_type = service_type or "MODEL_SERVICE"
        from django_abstract.registry import SERVICE_REGISTRY

        targets = hook_names if hook_names else self.hooks_list

        for name in targets:
            if hook_names and name not in self.hooks_list:
                continue

            target_service = SERVICE_REGISTRY.get(service_type, {}).get(name)
            if not target_service:
                target_service = SERVICE_REGISTRY.get("BARE_SERVICE", {}).get(name)

            if target_service and hasattr(target_service, "hook"):
                # Passes the SED directly, keeping 100% compatibility with Model Services
                target_service.hook(entry=entry or self.entry)
        return True

    def logging_hook(self, operation, e=None, **kwargs):
        error_message = (
            f"Failed logic operation [{operation}] with data {kwargs}. trace back: {e}"
        )
        return ErrorSuccessLogger().logging_check(
            operation=operation,
            service_data=self.get_class_info(),
            error_message=error_message,
        )
