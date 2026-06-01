# core utilities.py
import inspect
from dataclasses import dataclass, field
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.apps import apps
from functools import partial
from django.urls import resolve
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from django.db import models
import re
from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseRedirect, HttpResponse

def to_snake_case(name):
    # Insert underscore before capital letters (that are not at the start)
    # 1. Handle "XMLHttp" -> "XML_Http"
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # 2. Handle "MyClass" -> "My_Class"
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class ClassInfoProvider:

    def __init__(self):
        pass
    
    def get_class_info(self,):
        module_name = self.__module__
        data = {
            'method_name': inspect.currentframe().f_code.co_name,
            'app_name': apps.get_containing_app_config(module_name).name,
            'service_name': self.__class__.__name__,
        }
        return data
    @staticmethod
    def resolve_class_info(obj):
        module_name = obj.__module__
        data = {
            'method_name': inspect.currentframe().f_code.co_name,
            'app_name': apps.get_containing_app_config(module_name).name,
            'service_name': obj.__class__.__name__,
        }

        return data
    @classmethod
    def view_mixin_info(cls,):
        module_name = cls.__module__
        data = {
            'method_name': cls.service_method,
            'app_name': apps.get_containing_app_config(module_name).name,
            'service_name': cls.service_name,
            'domain': cls.domain,
            'action_name': cls.action_name,
            'view_name': cls.__name__,
            'bind_to_request': cls.bind_to_request,
        }
        return data

@dataclass
class ServiceEntryData:
    """to avoid random data layer manipulation only when actually pulled out"""
    model_name:str =field(default_factory=str)
    obj_id:str=field(default_factory=str)
    service_data:dict=field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict) # Input data (POST)
    errors: Dict[str, Any] = field(default_factory=dict)
    history: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def add_to_history(self):
        self.history[self.obj_id]={
            'model_name': self.model_name,
            'obj_id': self.obj_id,
            'service_data': self.service_data,
            'raw_data': self.raw_data,
            'errors': self.errors,
            'history': self.history,
        }
        return self
    
    @classmethod
    def load_obj_data(cls, obj,):
        if not obj:
            return cls()
        cls_obj = cls(
            
        model_name = to_snake_case(obj.__class__.__name__),
        obj_id = obj.id,
        raw_data = obj.__dict__,
        )
        return cls_obj


class ServiceDataOperator:
    def __init__(self,entry:ServiceEntryData):
        super().__init__()
        self.entry:ServiceEntryData = entry
    @classmethod
    def make_entry(cls, model_name:str=None, obj_id:str=None, service_data:dict=None, raw_data: Dict=None,):
        return cls(
            entry=ServiceEntryData(
                    model_name=model_name,
                    obj_idr=obj_id, 
                    service_data=service_data,
                    raw_data=raw_data,
                    )
            )
    
    def flush_updates(self, pending_updates):
        if pending_updates:
            self.pending_updates = pending_updates
            self._flush_updates()
        if self.pending_updates:
            self.force_flush()
        return self.entry
    
    def _flush_updates(self):
        """Flush pending updates to database"""
        try:
            self.entry.service_data.update(**self.pending_updates)
            self._last_save = timezone.now()
            self.pending_updates.clear()
            return self.entry, True
        except Exception as e:
            self.logging_hook(operation=f'UPDATE SHOPPING BEHAVIOR OF USER {self.shopping_behavior_obj.id}', error_message=f'Failed updating the shopping behavior of user {self.user.session} with data {self.pending_updates}. trace back: {e} ')
            return self.entry, False

    def force_flush(self):
        """Force flush pending updates"""
        return self._flush_updates()[1]

    def init_default_state(self):
        """Initialize default tracking state"""
        self.last_updated = None
        self.pending_updates = {}
    
    def should_update(self):
        """Check if we should proceed with update"""
        return self.pending_updates is not None or not {}

    def set_result(self, result:dict):
        self.entry.result_data = result
        return self

    def add_error(self, error_msg: str):
        self.entry.errors.append(error_msg)
        return self

    def has_errors(self) -> bool:
        return len(self.entry.errors) > 0

@dataclass
class EntryData:
    ip_address: str=field(default_factory=str)
    user_agent: str=field(default_factory=str)

    domain :str=field(default_factory=str)
    user_id: str =field(default_factory=str)   # User ID or Guest UUID
    timestamp: datetime = field(default_factory=datetime.now)
    status :str=field(default_factory=str)
    is_guest:bool=True
    is_banned: bool = False

class EntryDataOperator:
    def __init__(self,entry:EntryData):
        super().__init__()
        self.entry:EntryData = entry
    @classmethod
    def make_entry(cls, domain=None, actor_id=None, timestamp=None, status=None,):
        return cls(EntryData(domain=domain, actor_id=actor_id, timestamp=timestamp, status=status,))
    @property    
    def activate(self):
        """Activate the query."""
        self.entry.status = "activated"
        
    @property
    def deactivate(self):
        """Deactivate the query."""
        self.entry.status = "deactivated"
    
    @property
    def disable(self):
        """Explicitly disable (admin control)."""
        self.entry.status = "disabled"

@dataclass
class ControlEntryData:
    service_name: str=field(default_factory=str)      # Target Service
    service_domain: str=field(default_factory=str)      # Target Service
    operator: str = "default" # "add_item", "merge_cart"
    flags: Dict[str, bool] = field(default_factory=dict) # {skip_validation: True}
    related_flows: Dict[str,str] = field(default_factory=dict) # {"email:trigger_email", "inventory:update_inventory"}
    errors: Dict[str,Any] = field(default_factory=dict) 
    service_args: Dict[str,Any] = field(default_factory=dict) 
    actor_id: Optional[str] = None
    actor_role: str = "guest"

class ControlDataOperator:
    """Manages flow control and flags."""
    def __init__(self, entry: ControlEntryData):
        self.entry = entry

    def set_flag(self, key: str, value: bool = True):
        self.entry.flags[key] = value
        return self

    def has_flag(self, key: str) -> bool:
        return self.entry.flags.get(key, False)

    def switch_operator(self, new_operator: str):
        self.entry.operator = new_operator
        return self
    @classmethod
    def make_entry(cls, service_name: str=None, service_domain: str=None, operator: str=None, flags: Dict=None,related_flows: List=None):
        return cls(ControlEntryData(service_name=service_name, service_domain=service_domain, operator=operator, flags=flags, related_flows=related_flows,))

class EntryValidator:
    def __init__(self, entry, service_class):
        self.entry = entry
        self.service_class = service_class

    def is_operatable(self):
        # Implement your validation logic here
        # For example, check if the code is not empty
        if (
            not self.entry.flags["client"]
            or not self.entry.flags["admin"]
            or not self.entry.flags["service"]
        ):
            return False
        return True

    def can_run(self) -> bool:
        # Implement your validation logic here
        # For example, check if the code is not empty
        if self.is_operatable():
            return False
        can_run = self.service_class(self.entry).can_run()
        return bool(can_run)

    def service_args(self, arg, klass, is_service=True):
        if not self.entry.service_data["action"]:
            return False
        if self.is_operatable():
            if is_service:
                if self.entry.service_data[f"{arg}"]:
                    if not isinstance(self.entry.service_data[f"{arg}"], klass):
                        return False
                    return True
            else:
                if self.entry.obj_data[f"{arg}"]:
                    if not isinstance(self.entry.obj_data[f"{arg}"], klass):
                        return False
                    return True
            return False
        return False

@dataclass
class RequestPathObjectMapper:
    app: str=field(default_factory=str)
    
    list_url: list[str]=field(default_factory=list)
    extra: dict[str, str] = field(default_factory=dict)
    args: dict[str, str] = field(default_factory=dict)
    flags: dict[str, Any] = field(default_factory=dict)

    def is_none(
        self,
    ):
        attr_dict = self.__dict__
        if any([v is None for v in attr_dict.values()]):
            self.flags["is_none"] = [
                attr for attr in list(attr_dict.keys()) if attr is None
            ]
            return True
        else:
            self.flags["is_none"] = None
            return False

    def is_valid(
        self,
    ):
        if self.is_none():
            return False

        if not self.flags["is_none"]:
            return True
        else:
            return False

class Entry(ClassInfoProvider):
    def __init__(self, session_key=None,return_value=None,request=None):
        self.session_key = session_key
        self.return_value = return_value
        self.request = request
        self.help_data = {}
        self.entry_data: EntryData=EntryData()
        self.control_entry_data: ControlEntryData=ControlEntryData()
        self.service_entry_data: ServiceEntryData=ServiceEntryData()
        self.is_modified=False
        self.request_path_object_mapper: RequestPathObjectMapper = RequestPathObjectMapper()
        self.context_operator:EntryDataOperator=self.op_entry_data
        self.payload_operator:ServiceDataOperator=self.op_service_entry_data
        self.control_operator:ControlDataOperator=self.op_control_entry_data
        self.errors: Dict[str,Any] = {}
        self.system_infos = self.get_class_info()
        super().__init__()

    @property
    def op_entry_data(self) -> EntryDataOperator:
        """Access the Metadata Operator."""
        return EntryDataOperator(self.entry_data)

    @property
    def op_control_entry_data(self) -> ControlDataOperator:
        """Access the Control Flow Operator."""
        return ControlDataOperator(self.control_entry_data)

    @property
    def op_service_entry_data(self) -> ServiceDataOperator:
        """Access the Service/Payload Operator."""
        return ServiceDataOperator(self.service_entry_data)

    @classmethod
    def make_entry(cls, session_key,entry_data:dict=None, service_data:dict=None, control_data:dict=None,):
        """Builder to initialize all sub-structures."""
        new_cls =cls(session_key=session_key) 

        new_cls.entry_data=EntryData(**entry_data),
        new_cls.control_entry_data=ControlEntryData(**control_data),
        new_cls.service_entry_data=ServiceEntryData(**service_data)
        return new_cls

def resolve_entry_from_selector(object_attribute:str,):
    """
       Given an object, search for the specified object_attribute, and create an Entry object
       based on the provided query data. If the object_attribute is found, return an Entry
       with the corresponding selector name.

       Parameters:
       - obj: The object to search for the object_attribute in.
       - object_attribute: The object_attribute whose value will be matched. (obj.object_attribute)
       - query_obj_data: The data that queried from database (obj) used to create the EntryData for the Entry object.

       Returns:
       - An Entry object if a matching object_attribute is found, otherwise None.
       """
    entry_list = []
    if object_attribute in vars(global_dependency).keys():
        object_attribute_instance = getattr(global_dependency, object_attribute)
        query_data_set = object_attribute_instance.filter(is_active=True, is_disabled=False,)
        for query_obj_data in query_data_set:
            query_data = EntryData( name=query_obj_data.__class__.__name__.lower(), entry_id=query_obj_data.id, start_date=query_obj_data.start_date, end_date=query_obj_data.end_date, status="activated" if query_obj_data.is_active else "deactivated",)
            entry_list.append(Entry(selector_obj_name=object_attribute, query_obj=query_data))
        return entry_list
    else:
        return list()

def get_view_class_and_args(request):
    """
    Returns the view class (or function) and arguments (args, kwargs) from the given request.
    
    :param request: Django HttpRequest object
    :return: dict with 'view_func', 'view_class', 'args', and 'kwargs'
    """
    resolver_match = resolve(request.path_info)

    view_func = resolver_match.func
    view_class = None

    # Check if it's a class-based view
    if hasattr(view_func, 'view_class'):
        view_class = view_func.view_class
    elif hasattr(view_func, '__self__') and hasattr(view_func.__self__, '__class__'):
        # Handles already-instantiated view (e.g. DRF ViewSet actions)
        view_class = view_func.__self__.__class__
    else:
        # For function-based views, view_class will remain None
        pass

    return {
        'view_func': view_func,
        'view_class': view_class,
        'args': resolver_match.args,
        'kwargs': resolver_match.kwargs,
    }

class ModelFieldChecker(ClassInfoProvider):
    """Utility class for checking model field types"""

    def __init__(self):
        self.utility_infos = self.get_class_info()
        super().__init__()

    @classmethod
    def has_image_field(cls, model: models.Model) -> bool:
        """
        Check if a model contains any ImageField
        Args:
            model: Name of the model
        Returns:
            bool: True if model has at least one ImageField
        Raises:
            LookupError: If model cannot be found
        """
        try:
            return cls._has_field_type(model, models.ImageField)
        except LookupError as e:
            raise LookupError(f"Model {model}.ImageField not found") from e

    @classmethod
    def get_image_fields(cls, model_class) -> list:
        """
        Get all ImageField names in a model
        Args:
            model_class: Django model class
        Returns:
            list: Names of all ImageFields
        """
        return cls._get_fields_of_type(model_class, models.ImageField)

    @classmethod
    def has_specific_image_field(cls, model_class, field_name: str) -> bool:
        """
        Check if a specific field is an ImageField
        Args:
            model_class: Django model class
            field_name: Name of the field to check
        Returns:
            bool: True if the field exists and is an ImageField
        """
        try:
            field = model_class._meta.get_field(field_name)
            return isinstance(field, models.ImageField)
        except FieldDoesNotExist:
            return False

    @staticmethod
    def _has_field_type(model_class, field_type) -> bool:
        """Generic field type checker"""
        return any(
            isinstance(field, field_type)
            for field in model_class._meta.get_fields()
            if hasattr(field, "upload_to")  # Additional check for FileField/ImageField
        )

    @staticmethod
    def _get_fields_of_type(model_class, field_type) -> list:
        """Get all fields of specific type"""
        return [
            field.name
            for field in model_class._meta.get_fields()
            if isinstance(field, field_type)
        ]

def admin_or_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

class AdminOrStaffMixin:

    def __init__(self):
        super().__init__()

    @method_decorator(user_passes_test(admin_or_staff))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
def admin_and_staff(user):
    return user.is_authenticated and (user.is_staff and user.is_superuser)

class AdminAndStaffMixin:

    def __init__(self):
        super().__init__()

    @method_decorator(user_passes_test(admin_and_staff))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class ModelRelatedExceptionMixin:
    """Mixin to provide related model info in exceptions"""

    def __init__(self,model_instance, *args, **kwargs):
        super().__init__()
        self.model_instance = model_instance

    def get_related_model_info(self, model_instance=None):
        """Extract related model info for better exception context"""
        model_instance = model_instance or self.model_instance
        related_info = {}
        for field in model_instance._meta.get_fields():
            if field.is_relation and hasattr(model_instance, field.name):
                related_obj = getattr(model_instance, field.name)
                if related_obj is not None:
                    related_info[field.name] = {
                        'model': related_obj.__class__.__name__,
                        'id': getattr(related_obj, 'id', None),
                    }
        return related_info

def bind(config, request, **kwargs):
    if config["bind"]:
        # 2. Build and Bind Entry
        # Resolve Actor (Relies on GuestMiddleware having run)
        is_guest = not request.user.is_authenticated
        actor = request.user if not is_guest else getattr(request, "guest", None)
        actor_id = str(actor.id) if hasattr(actor, "id") else None
        # 3. Attach to Request
        # We flag is_modified=True immediately so Middleware knows this request
        # interacted with the GMES ecosystem (useful for logging/cookies)
        raw_data = {**request.GET.dict(), **request.POST.dict(), **kwargs}  # URL Params

        request.GMS_OBJECT.entry.entry_data = EntryData(
            domain=config["domain"], user_id=actor_id, is_guest=is_guest
        )
        request.GMS_OBJECT.entry.service_entry_data = ServiceEntryData(
            model_name=config["service_name"].strip("Service"), raw_data=raw_data
        )
        request.GMS_OBJECT.entry.control_entry_data = ControlEntryData(
            service_name=config["service_name"]
        )
        request.GMS_OBJECT.entry.help_data = config
        request.GMS_OBJECT.entry.is_modified = True
        # request.GMS_OBJECT.entry = entry
        request.GMS_OBJECT.VIEW.view_info = config["view_info"]
    return None

class EntryBindingMixin(ClassInfoProvider):
    """
    Mixin that automatically binds a GMES Entry to the request based on Class Metadata.
    Uses __init_subclass__ to pre-validate and configure the view at definition time.
    """

    # Defaults
    domain: str = None
    service_name: str = None
    service_method: str = None
    action_name: str = None
    bind_to_request: bool = True
    view_info: dict = None
    # Storage for class-level config (populated by __init_subclass__)
    _gmes_config = {
        "bind_to_request": bind_to_request,
        "domain": (domain or str()),
        "service_name": (service_name or str()),
        "action_name": (action_name or str()),
        "service_method": (service_method or str()),
        "view_info": (view_info or dict()),
    }

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # 1. Extract Configuration
        # We capture these at class creation time
        bind_to_request = getattr(cls, "bind_to_request", None) or str()
        domain = getattr(cls, "domain", None) or str()
        service = getattr(cls, "service_name", None) or str()
        action = getattr(cls, "action_name", None) or str()
        method = getattr(cls, "service_method", None) or str()
        url_name = getattr(cls, "url_name", None)

        def get_view_info(cls):
            return cls.view_mixin_info()

        view_info = partial(get_view_info, cls)
        # 2. Validation (Fail Fast)
        if bind_to_request:
            if not domain:
                # Optional: Strict check or allow generic domain
                # raise ImproperlyConfigured(f"{cls.__name__} requires 'domain' when bind_to_request=True")
                pass

        # 3. Store in optimized dictionary for runtime access
        cls._gmes_config = {
            "bind": bind_to_request,
            "domain": domain,
            "service_name": service,
            "action_name": action,
            "service_method": method,
            "view_info": view_info,
        }

        if url_name:
            register_abstract_view(
                url_name, partial(bind, cls._gmes_config, request=None)
            )

    def dispatch(self, request, *args, **kwargs):
        # 1. Check Binding Flag
        # Access class-level config dict (faster than getattr)
        bind(self._gmes_config, request, **kwargs)

        return super().dispatch(request, *args, **kwargs)

@dataclass
class ExtractRequestDataUtilities:
    """
    Extracts raw HTTP request data (IP, Agent, Path, Payload).
    Fills the Entry object and passes extra contextual info to the RequestPathObjectMapper.
    """

    request: Any  # Expects Django HttpRequest

    @property
    def ip_address(self) -> str:
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return self.request.META.get("REMOTE_ADDR", "Unknown")

    @property
    def user_agent(self) -> str:
        return self.request.META.get("HTTP_USER_AGENT", "Unknown")

    @property
    def path(self) -> str:
        return self.request.path

    @property
    def method(self) -> str:
        return self.request.method

    @property
    def post_data(self) -> dict:
        return (
            self.request.POST.dict()
            if self.request.method in ["POST", "PUT", "PATCH"]
            else {}
        )

    @property
    def get_data(self) -> dict:
        return self.request.GET.dict()

    @property
    def session_data(self) -> dict:
        if hasattr(self.request, "session"):
            if not self.request.session.session_key:
                self.request.session.create()
            return {
                "session_key": self.request.session.session_key,
                **dict(self.request.session.items()),
            }
        return {}

    def populate_entry(self, entry=None):
        """
        Updates the Entry object with request context and
        injects extra info (IP, agent) into the RequestPathObjectMapper (RPOM).
        """
        session_key = self.session_data.get("session_key")

        if entry is None:
            # Assuming Entry is already imported/defined in this file
            entry = Entry(session_key=session_key)
        else:
            entry.session_key = session_key

        # 1. Update EntryData (Actor/Guest Context)
        entry.entry_data.is_guest = not self.request.user.is_authenticated
        if self.request.user.is_authenticated:
            entry.entry_data.user_id = str(self.request.user.id)
        else:
            entry.entry_data.user_id = session_key

        # 2. Build RPOM and inject extra information into the 'extra' dict
        path_parts = [p for p in self.path.split("/") if p]
        app_name = path_parts[0] if path_parts else "unknown"

        rpom = RequestPathObjectMapper(
            app=app_name,
            list_url=path_parts,
            args=(
                self.post_data
                if self.method in ["POST", "PUT", "PATCH"]
                else self.get_data
            ),
            extra={
                "ip_address": self.ip_address,
                "user_agent": self.user_agent,
                "method": self.method,
                "full_path": self.path,
            },
        )

        # 3. Attach RPOM to the Master Entry and Control Data
        entry.request_path_object_mapper = rpom
        entry.control_entry_data.request_path_object_mapper = rpom

        # 4. Push payload to ServiceEntryData raw_data
        entry.service_entry_data.raw_data = rpom.args

        return entry

class HtmxLoginRequiredMixin(AccessMixin):
    """
    Verify that the current user is authenticated.
    If not, natively redirect them, supporting HTMX HX-Redirect.
    """

    def handle_no_permission(self):
        # This is where Django usually sends the user to the login page
        url = self.get_login_url()

        # Check if the request was made by HTMX
        if self.request.headers.get("HX-Request") == "true":
            # Tell HTMX to force the browser to navigate
            response = HttpResponse(status=200)
            response["HX-Redirect"] = url
            return response

        # If it's a normal browser request, do the native Django 302 redirect
        return HttpResponseRedirect(url)
