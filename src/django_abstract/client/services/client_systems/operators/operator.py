from django_abstract.base_operator import Operator
from django_abstract.client.services.operators.operator_regestry import  register_operator

@register_operator
class SessionOperator(Operator):
    domain='session'
    def __init__(self, entry):
        super().__init__(session_key=entry.session_key)
        self._sub_systems = self._resolve_domain_systems()
        self.system_args = entry.args
    
