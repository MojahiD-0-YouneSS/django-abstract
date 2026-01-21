from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ImproperlyConfigured
from django_abstract.utilities import (
    Entry, 
    ClassInfoProvider,
    EntryData,ServiceEntryData,ControlEntryData,
    )
from functools import partial

ABSTRACT_VIEW_REGESTRY = {}
def register_abstract_view(url_name,bind_func):
    ABSTRACT_VIEW_REGESTRY[url_name]=bind_func
    return None
def bind(config,request,**kwargs):
    if config['bind']:
        # 2. Build and Bind Entry
            # Resolve Actor (Relies on GuestMiddleware having run)
        is_guest = not request.user.is_authenticated
        actor = request.user if not is_guest else getattr(request, 'guest', None)
        actor_id = str(actor.id) if hasattr(actor, 'id') else None
        # 3. Attach to Request
        # We flag is_modified=True immediately so Middleware knows this request
        # interacted with the GMES ecosystem (useful for logging/cookies)
        raw_data = {
        **request.GET.dict(), 
        **request.POST.dict(), 
        **kwargs  # URL Params
        }

        request.GMS_OBJECT.entry.entry_data=EntryData(
                domain=config['domain'],
                user_id=actor_id,
                is_guest=is_guest
            )
        request.GMS_OBJECT.entry.service_entry_data=ServiceEntryData(
            model_name=config['service_name'].strip('Service'),
                raw_data=raw_data
            )
        request.GMS_OBJECT.entry.control_entry_data=ControlEntryData(
                service_name=config['service_name']
            )
        request.GMS_OBJECT.entry.help_data = config
        request.GMS_OBJECT.entry.is_modified = True 
        # request.GMS_OBJECT.entry = entry
        request.GMS_OBJECT.VIEW.view_info = config['view_info']
    return None 

class EntryBindingMixin(ClassInfoProvider):
    """
    Mixin that automatically binds a GMES Entry to the request based on Class Metadata.
    Uses __init_subclass__ to pre-validate and configure the view at definition time.
    """
    # Defaults
    domain: str = None
    service_name: str = None
    service_method:str=None
    action_name:str=None
    bind_to_request: bool = True
    view_info:dict=None
    # Storage for class-level config (populated by __init_subclass__)
    _gmes_config =  {
            'bind_to_request': bind_to_request,
            'domain': (domain or str()),
            'service_name': (service_name or str()),
            'action_name': (action_name or str()),
            'service_method': (service_method or str()),
            'view_info':(view_info or dict()),
        }

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        
        # 1. Extract Configuration
        # We capture these at class creation time
        bind_to_request = getattr(cls, 'bind_to_request', None) or str()
        domain = getattr(cls, 'domain', None) or str()
        service = getattr(cls, 'service_name', None) or str()
        action = getattr(cls, 'action_name', None) or str()
        method = getattr(cls, 'service_method', None) or str()
        url_name = getattr(cls, 'url_name', None)
        def get_view_info(cls):
            return cls.view_mixin_info()
        view_info = partial(get_view_info,cls)
        # 2. Validation (Fail Fast)
        if bind_to_request:
            if not domain:
                # Optional: Strict check or allow generic domain
                # raise ImproperlyConfigured(f"{cls.__name__} requires 'domain' when bind_to_request=True")
                pass

        # 3. Store in optimized dictionary for runtime access
        cls._gmes_config = {
            'bind': bind_to_request,
            'domain': domain,
            'service_name': service,
            'action_name': action,
            'service_method': method,
            'view_info':view_info
        }

        if url_name:
            register_abstract_view(url_name,partial(bind,cls._gmes_config,request=None))

    def dispatch(self, request, *args, **kwargs):
        # 1. Check Binding Flag
        # Access class-level config dict (faster than getattr)
        bind(self._gmes_config,request,**kwargs)
       
        return super().dispatch(request, *args, **kwargs)


class AbstractViewClass(EntryBindingMixin, View):
    """
    Standard Base View for GMES-enabled endpoints."""
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
