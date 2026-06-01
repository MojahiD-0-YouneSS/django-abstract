from django_abstract.utilities import to_snake_case
from dataclasses import dataclass, field
from typing import List, Callable, Optional
from functools import wraps
from django_abstract.exceptions import ServiceException

GLOBAL_REGISTRY = {}

# GLOBAL_REGISTRY => {'app':dependency['selectors':{'name':class},'creators':{'name':class}]}

def creator_selector(name=None, dependency=None,):
    """
    used in case registing from a model
    """
    from django_abstract.base.base_selector import BaseSelector
    from django_abstract.base.base_creator import BaseCreator
    def wrapper(cls):

        select_key = name or f"select_{to_snake_case(cls.__name__)}"
        create_key = name or f"create_{to_snake_case(cls.__name__)}"
        select_name = f"{cls.__name__}Selector"
        create_name = f"{cls.__name__}Creator"

        if not dependency:
            raise NotImplementedError(f"Dependency for ''{dependency.__name__}'' service must be provided")

        if not hasattr(dependency, "selectors") or not hasattr(dependency, "creators"):
            raise NotImplementedError(f"Dependency ''{dependency.__name__}'' does not have selectors or creators")

        def dynamic_init(self, ):
            BaseSelector.__init__(self, model_class=cls)

        class_attrs = {
            "__module__": __name__,
            '__init__': dynamic_init,
        }
        if dependency.app_name in GLOBAL_REGISTRY:
            selector_class = type(select_name, (BaseSelector,), class_attrs)
            creator_class = type(create_name, (BaseCreator,), class_attrs)

            GLOBAL_REGISTRY[dependency.app_name].selectors.update({select_key: selector_class})
            GLOBAL_REGISTRY[dependency.app_name].creators.update({create_key: creator_class})
        else:
            selector_class = type(select_name, (BaseSelector,), class_attrs)
            creator_class = type(create_name, (BaseCreator,), class_attrs)
            dependency.selectors = {select_key: selector_class}
            dependency.creators = {create_key: creator_class}
            GLOBAL_REGISTRY[dependency.app_name] = dependency
        dependency.model_class=cls
        return cls
    return wrapper

SELECTOR_REGISTRY = {}

def register_selector(name=None, dependency=None):
    """
    used in case registing from a selector
    """
    def wrapper(cls):
        key = name or cls.__name__.replace("Selector", "").lower()

        if dependency.app_name in SELECTOR_REGISTRY:
            SELECTOR_REGISTRY[dependency.app_name].selectors[key] = cls
        if not dependency.app_name in SELECTOR_REGISTRY:
            dependency.selectors={key:cls}
            SELECTOR_REGISTRY[dependency.app_name] = dependency
        return cls
    return wrapper

CREATOR_REGISTRY = {}

def register_creator(name=None, dependency=None):
    """
    used in case registing from a creator
    """
    def wrapper(cls):
        key = name or cls.__name__.replace("Creator", "").lower()
        if dependency.app_name in CREATOR_REGISTRY:
            CREATOR_REGISTRY[dependency.app_name].creators[key] = cls
        if not dependency.app_name in CREATOR_REGISTRY:
            dependency.creators={key:cls}
            CREATOR_REGISTRY[dependency.app_name] = dependency

        return cls
    return wrapper

ABSTRACT_VIEW_REGISTRY = {}


def register_abstract_view(url_name, bind_func):
    ABSTRACT_VIEW_REGISTRY[url_name] = bind_func
    return None

SERVICE_REGISTRY = {
    "MODEL_SERVICE":{},
    "BARE_SERVICE":{}
}


def register_service(name=None, service_type=None):
    """
    used in case registing from a creator
    """

    from django_abstract.base.base_model_service import BaseModelService
    from django_abstract.base.base_service import BaseService

    def wrapper(cls):
        resolved_type = service_type

        if not resolved_type:
            if issubclass(cls,BaseModelService):
                resolved_type = "MODEL_SERVICE"
            else:
                resolved_type='BARE_SERVICE'

        key = name or to_snake_case(cls.__name__)
        SERVICE_REGISTRY[resolved_type][key]=cls
        return cls

    return wrapper

OPERATOR_REGISTRY = {}

GLOBAL_OPERATOR_REGISTRY = {}


def register_operator():
    def wrapper(cls):
        if not cls.__name__ in OPERATOR_REGISTRY:
            OPERATOR_REGISTRY[to_snake_case(cls.__name__)] = cls
        if hasattr(cls, 'app_name'):
            if cls.app_name not in GLOBAL_OPERATOR_REGISTRY:
                GLOBAL_OPERATOR_REGISTRY[cls.app_name]={}
                GLOBAL_OPERATOR_REGISTRY[cls.app_name][to_snake_case(cls.__name__)]=cls
            else:
                GLOBAL_OPERATOR_REGISTRY[cls.app_name][to_snake_case(cls.__name__)]=cls

        return cls

    return wrapper


SYSTEM_REGISTRY = {
    'MODEL_SYSTEM':{},
    'BARE_SYSTEM':{},
}
def register_system():
    def wrapper(cls):
        from django_abstract.base.base_model_system import BaseModelSystem
        # from django_abstract.base.base_system import BaseSystem

        if issubclass(cls,BaseModelSystem):

            resolved_type = 'MODEL_SYSTEM'
        else:
            resolved_type = 'BARE_SYSTEM'

        SYSTEM_REGISTRY[resolved_type][to_snake_case(cls.__name__)] = cls
        return cls

    return wrapper


def get_app_dependency(app_name:str):
    return GLOBAL_REGISTRY.get(app_name)

def get_app_select_dependency(app_name:str):
    return SELECTOR_REGISTRY.get(app_name)

def get_app_create_dependency(app_name:str):
    return CREATOR_REGISTRY.get(app_name)

def get_abstract_view(app_name:str):
    return ABSTRACT_VIEW_REGISTRY.get(app_name)

def get_service(service_name:str):
    if service_name in SERVICE_REGISTRY["MODEL_SERVICE"].keys():
        return SERVICE_REGISTRY["MODEL_SERVICE"].get(service_name)
    else:
        return SERVICE_REGISTRY["BARE_SERVICE"].get(service_name)

def get_system(system_name:str):
    if system_name in SYSTEM_REGISTRY["Model_SYSTEM"].keys():
        return SYSTEM_REGISTRY["Model_SYSTEM"].get(system_name)
    else:
        return SYSTEM_REGISTRY["BARE_SYSTEM"].get(system_name)

def get_operator(operator_name:str):
    return OPERATOR_REGISTRY.get(operator_name)


@dataclass
class ServiceSettings:

    RESERVED_DB_METHODS: dict[str, list] = field(
        default_factory=lambda: {
            "read_entry": [],
            "delete_entry": [],
            "create_entry": [],
        }
    )
    MINIMUM_WRITE_FIELDS: list = field(default_factory=list)
    SERVICE_DOMAIN_FIELDS: list = field(default_factory=list)
    VALID_FIELDS: dict = field(default_factory=dict)
    VALID_FIELDS_PER_ACTION: dict = field(default_factory=dict)
    MINIMUM_READ_FIELDS: list = field(default_factory=list)
    VALID_FIELDS_PER_ACTION: dict = field(default_factory=dict)


def service_settings(settings: Optional[ServiceSettings] = None):
    """
    Injects the ServiceSettings into the decorated method (usually load_settings).

    Usage:
    @service_settings(settings=ServiceSettings(MINIMUM_WRITE_FIELDS=['id']))
    def load_settings(self, settings):
        return super().load_settings(settings)
    """
    if not settings:
        settings = ServiceSettings()

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Pass the settings to the decorated method while preserving self
            return func(self, settings, *args, **kwargs)

        return wrapper

    return decorator


def action_method_fields(*fields):
    """
    Method decorator that validates required fields and injects them
    into the action method as kwargs, allowing native Python arguments
    instead of using self.get_method_args().

    Usage:
    @action_method_fields("variant_id", "quantity")
    def add_item(self, variant_id, quantity):
        ...
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 1. Extract the payload envelope
            data = self.entry.service_data if hasattr(self, "entry") else {}

            # 2. Validation Phase: Check required fields
            missing_fields = [f for f in fields if f not in data and f not in kwargs]

            if missing_fields:
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                if hasattr(self, "entry"):
                    self.entry.errors[func.__name__] = error_msg
                return False

            # 3. Injection Phase: Auto-inject fields into kwargs for the method signature
            for f in fields:
                if f not in kwargs and f in data:
                    kwargs[f] = data[f]

            # 4. Execution Phase with Error Isolation
            try:
                # Execute the actual typed Python method with injected kwargs
                result = func(self, *args, **kwargs)

                # Auto-hydrate the behavior state if a dictionary is returned
                if isinstance(result, dict) and hasattr(self, "behavior"):
                    self.behavior.service_data.update(result)

                return True

            except ServiceException as e:
                # Graceful business logic failure
                if hasattr(self, "entry"):
                    self.entry.errors[func.__name__] = str(e)
                return False

            except Exception as e:
                # Unhandled system crash
                if hasattr(self, "entry"):
                    self.entry.errors["fatal"] = f"Service execution failed: {str(e)}"
                return False

        return wrapper

    return decorator
