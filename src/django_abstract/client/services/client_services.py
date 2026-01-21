from django_abstract.client.dependencies import get_dependency_manager
from django_abstract.client.services.client_systems.operators.operator_regestry import register_service
from django_abstract.log.utilities import ErrorSuccessLogger
from django.utils import timezone
from django_abstract.utilities import ServiceEntryData, ServiceDataOperator
from django_abstract.base_operator_service import BaseOperatorService

CDM = get_dependency_manager()

class IdentityCheckService(BaseOperatorService):
    
    domain='session'
    model_dependency=CDM.select_abstract_guest_identity
    def __init__(self, session_key,*args,**kwargs,):
        super().__init__(
            session_key=session_key,
            *args,**kwargs,
        )
        self.session_key = session_key
        self.operator.init_default_state()
        self.hooks_list = []
        
    class IdentityCheckValidator(BaseOperatorService.BaseServiceValidator):
        _SERVICE_DOMAIN_FIELDS = [
                'session_key',
                'ip_address',
                'user_agent',
                'last_active_at',
                'is_converted',
                'converted_user',
            ]
        def __init__(self, **data):
            self.identity = data
            super().__init__(**self.identity)

    validator=IdentityCheckValidator
    def run(self, **kwargs):
        """
        Core update method with bulk operation support
        Returns tuple: (updated_object, success_bool)
        """

        try:
            return self.run_skeleten(**kwargs)
        except Exception as e:
            self.logging_hook(operation=f'UPDATE {self.entry.model_name.upper()}', e=e, **kwargs)
            
    def can_run(self,model_name, **kwargs) -> bool:
        validator =  self.validator(entry=self.entry)
        flag = validator.run(method_name=model_name, data=kwargs)
        return flag


