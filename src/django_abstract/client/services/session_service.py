from django_abstract.client.dependencies import get_dependency_manager
from django_abstract.client.services.client_systems.operators.operator_regestry import register_service
from django_abstract.utilities import ServiceEntryData, ServiceDataOperator
from django.utils import timezone
from django_abstract.base_operator_service import BaseOperatorService

CMD = get_dependency_manager()

class BannedUserService(BaseOperatorService):
    domain='session'
    model_dependency=CMD.select_abstract_banned_user
    def __init__(self, session_key,*args,**kwargs,):
        super().__init__(
            session_key=session_key,
            *args,**kwargs,
        )
        
        self.session_key = session_key
        self.operator.init_default_state()
        self.hooks_list = []
    class BannedUserValidator(BaseOperatorService.BaseServiceValidator):
        _SERVICE_DOMAIN_FIELDS = [
            'session_key',
            'reason',
            'banned_at',
            'banned_until',
            ] 
            
        def __init__(self, **data):
            self.user_status = data
            super().__init__(**self.user_status)
        
    validator=BannedUserValidator
    def run(self, **kwargs):
        """
        Core update method with bulk operation support
        Returns tuple: (updated_object, success_bool)
        """
        try:
            return self.run_skeleten(**kwargs)
        except Exception as e:
            self.logging_hook(operation=f'UPDATE SESSION METRICS', e=e, **kwargs)
            raise ValueError("Either user or session_key must be provided")
        
    def can_run(self,model_name, **kwargs) -> bool:
        
        validator =  self.validator(entry=self.entry)
        flag = validator.run(method_name=model_name, data=kwargs)
        """if flag:
            self.entry.service_data = validator.behavior.service_data"""
        return flag

class SessionLinkService(BaseOperatorService):
    domain='session'
    model_dependency=CMD.create_abstract_session_link
    def __init__(self, session_key,*args,**kwargs):
        super().__init__(
            session_key=session_key,
            *args,**kwargs,
        )
        self.session_key = session_key
        self.operator.init_default_state()
        self.hooks_list = []
        
    class SessionLinkServiceValidator(BaseOperatorService.BaseServiceValidator):
        _MINIMUM_WRITE_FIELDS = ['abstract_guest_user_id','user']
        _SERVICE_DOMAIN_FIELDS = [
            'user',
            'abstract_guest_user',
            'curent_session_key',
            'previous_session_key',
            'merged_at',
            'session_count',
            'shared_device_hash',
            ]         
        def __init__(self, **data):
            self.session_link = data
            super().__init__(**self.session_link)
                     
    validator=SessionLinkServiceValidator
    
    def run(self, **kwargs):
        """
        Core update method with bulk operation support
        Returns tuple: (updated_object, success_bool)
        """
        try:
            return self.run_skeleten(**kwargs)
        except Exception as e:
            self.logging_hook(operation=f'UPDATE LINK {self.entry.model_name.upper()}', e=e, **kwargs)
            return self.entry, False
        
    def can_run(self,model_name, **kwargs) -> bool:
        validator =  self.validator(entry=self.entry)
        flag = validator.run(method_name=model_name, data=kwargs)
        return flag

class SessionMetricsService(BaseOperatorService):
    domain='session'
    model_dependency=CMD.select_abstract_session_metrics
    
    def __init__(self, session_key,*args,**kwargs,):
        super().__init__(
            session_key,
            *args,**kwargs,
        )
        
        self.session_key = session_key
        self.operator.init_default_state()
        self.hooks_list = []

    class SessionMetricsValidator(BaseOperatorService.BaseServiceValidator):
        _MINIMUM_WRITE_FIELDS   = ['ip_address']
        _SERVICE_DOMAIN_FIELDS = [
                'session_key',
                'ip_address',
                'user_agent',
                'shared_device_hash',
                'referrer',
                'start_time',
                'end_time',
                'pages_visited',
                'interactions_count',
                'conversion_occurred',
                'metadata',            
            ]
        def __init__(self, **data):
            self.metrics = data
            super().__init__(**self.metrics)
       
    validator=SessionMetricsValidator
    def run(self, **kwargs):
        """
        Core update method with bulk operation support
        Returns tuple: (updated_object, success_bool)
        """

        try:
            return self.run_skeleten(**kwargs)
        except Exception as e:
            self.logging_hook(operation=f'UPDATE SESSION METRICS', e=e, **kwargs)
            raise ValueError("Either user or session_key must be provided")
        
    def can_run(self,model_name, **kwargs) -> bool:
        validator =  self.validator(entry=self.entry)
        flag = validator.run(method_name=model_name, data=kwargs)
        return flag
