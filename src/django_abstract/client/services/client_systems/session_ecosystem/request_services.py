from typing import Any
from django_abstract.utilities import ClassInfoProvider
from django_abstract.utilities import (ServiceEntryData, Entry, ControlEntryData,RequestPathObjectMapper,)
from django.utils.text import slugify
from django.apps import apps

class UrlMapper(ClassInfoProvider):
    """
    This class is responsible for mapping URLs to their corresponding service names and arguments.
    It provides methods to extract the service name, arguments, and flags from the URL.
    """
    def __init__(self, request,):
        super().__init__()
        self.request = request  # Placeholder for session data
        self.view_info = request.GMS_OBJECT.VIEW.view_info() # Placeholder for session data
        self.mapped_url = None  # Placeholder for mapped URL
        self.request_path_obj = self._prepare_path_obj(self.request.path) # Placeholder for session data
        if self.request_path_obj:
            self.scan_request()

    def scan_request(self,):
        path = self.request.path
        parts = []
        for point in self.request_path_obj.list_url[1:]:
            if any(char.isdigit() for char in point):
                break
            parts.append(point)
        action_name = '_'.join(parts)
      
        args=self.request.POST if self.request.method == 'POST' else self.request.GET
        
        self.request_path_obj.action_name = action_name
        self.request_path_obj.args = args
        self.request_path_obj.extra['session_key'] = self.request.session.session_key
        self.request_path_obj.flags['crud_method'] = slugify( str(self.view_info['service_name'])).split('_')[0]

        self.request_path_obj.is_none()
        self.mapped_url = path
        return path
    
    def _prepare_path_obj(self, path):
        return RequestPathObjectMapper(
            app=self.view_info['app_name'],
            list_url=path.split('/'),
            service_name_slug=slugify(str(self.view_info['service_name'])),
            service_name=str(self.view_info['service_name']).replace('View', 'Service',),
            model_name=str(self.view_info['service_name']).strip('View',),
            action_name=str(self.view_info['action_name']),
            flags={'service':True,}
            )
    
    def _validaate_target_models(self,):
        models = [''.join([a[0].upper() for a in x.split('_')]) for x in self.request.POST.keys()]
        if models:
            ready_models:list[bool] = []
            for model_name in models:
                try:
                    model_class = apps.get_model(self.request_path_obj.app, model_name)
                    if model_class:
                        ready_models.append(True)
                except LookupError:
                    ready_models.append(False)
            return all(ready_models),models
        else:
            return False, models

    def is_url_mapping_valid(self,):
        if not self.request_path_obj:
            return False
        if self.request_path_obj.is_none():
            return False
        else:
            return True
    def get_entry_version(self,):
        
        entry=Entry(session_key=self.request_path_obj.extra['session_key'])
        entry.entry_data.user_id=self.request.user.id
        entry.service_entry_data.model_name = self.request_path_obj.model_name
        entry.service_entry_data.obj_id = None
        entry.control_entry_data.request_path_object_mapper=self.request_path_obj
        entry.control_entry_data.service_name=self.request_path_obj.service_name
        entry.service_entry_data.service_data['session_data']=dict(self.request.session)
        entry.service_entry_data.service_data['ip_address']=self.get_client_ip()
        
        return entry
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # The first IP in the list is typically the original client IP
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            # Fallback for direct connections
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
