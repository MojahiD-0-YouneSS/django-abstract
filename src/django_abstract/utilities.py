# core utilities.py
import inspect
from dataclasses import dataclass, field
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.apps import apps
from datetime import datetime, date
from typing import (
    Dict, List, Any,
)
import re
from types import SimpleNamespace

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
        cls.model_name = to_snake_case(obj.__class__.__name__)
        cls.obj_id = obj.id
        cls.raw_data = obj.__dict__
        cls.service_data=dict()
        cls.raw_data=dict()
        cls.errors=dict()
        return cls
    

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
    domain :str=field(default_factory=str)
    user_id: str =field(default_factory=str)   # User ID or Guest UUID
    timestamp: datetime = field(default_factory=datetime.now)
    status :str=field(default_factory=str)
    is_guest:bool=True

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
    related_flows: Dict[str,str] = field(default_factory=dict) # {"emain:trigger_email", "inventory:update_inventory"}
    request_path_object_mapper:Any = None
    
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

class Entry(ClassInfoProvider):
    def __init__(self, session_key=None,return_value=None):
        self.session_key = session_key
        self.return_value = return_value
        self.help_data = {}
        self.entry_data: EntryData=EntryData()
        self.control_entry_data: ControlEntryData=ControlEntryData()
        self.service_entry_data: ServiceEntryData=ServiceEntryData()
        self.is_modified=False
        self.context_operator:EntryDataOperator=self.op_entry_data
        self.payload_operator:ServiceDataOperator=self.op_service_entry_data
        self.control_operator:ControlDataOperator=self.op_control_entry_data
        
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

@dataclass
class GuestRequestObject:
    empty:bool=False
    entry:Entry=  field(default_factory=Entry)
    VIEW:SimpleNamespace =  field(default_factory=SimpleNamespace)
    guest_response:dict =  field(default_factory=dict)
    ASM:Any = None
    
@dataclass
class RequestPathObjectMapper:
    app:str
    action_name: str
    list_url:list[str]
    service_name_slug: str
    service_name: str
    model_name: str
    
    extra:dict[str,str]=field(default_factory=dict)
    args:dict[str,str]=field(default_factory=dict)
    flags:dict[str,Any]=field(default_factory=dict)
    
    def is_none(self,):
        attr_dict = self.__dict__
        if any([v is None for v in attr_dict.values()]):
            self.flags['is_none'] = [attr for attr in list(attr_dict.keys()) if attr is None]
            return True 
        else:
            self.flags['is_none'] = None
            return False
    def is_valid(self,):
        if self.is_none():
            return False
        
        if not self.flags['is_none']:
            return True
        else:
            return False

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
