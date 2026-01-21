from abc import ABC
from django_abstract.client.services.operators.operator_regestry import  SYSTEM_REGISTRY

class BasAbstractOperator(ABC):
    """
    All guest operators must inherit this class.
    """
    def __init__(self, session_key=None,domain=None):
        self.session_key = session_key
        self.domain=domain
    def run(self):
        """
        Default run method. Should be overridden.
        """
        raise NotImplementedError

    def can_run(self):
        """
        Optional hook for conditional execution, e.g., time-sensitive or based on data.
        """
        raise NotImplementedError
class BaseOperator(BasAbstractOperator):
    """
    All guest operators must inherit this class.
    """
    def __init__(self, session_key=None,domain=None):
        self.session_key = session_key
        self.domain=domain
    def _resolve_domain_systems(self,):
        try:
            return SYSTEM_REGISTRY[self.domain]
        except:
            raise NotImplementedError('needs OperatorException')
    def can_run(self):
        return bool(self.session_key)

    def run(self):
        if not self.can_run():
            return None
        system = self._sub_systems.get(entry.service_name,None)
        args = self.system_args.get(system.__namne__, {})
        if all(args.values()) and callable(system):
            instance = system(**args)
            if hasattr(instance, 'can_run'):
#                    logger.info(f"Running {system.__name__} for Guest {self.session_key}")
                try:
                    is_ready = instance.can_run()
                    if is_ready:
                        instance.run()
                except Exception as e:
                    # logger.error(f"Error running {system.__name__}: {e}")
                    print(e)

    def args_checks(self):
        return self.system_args


def get_operator(session_key):
    return BaseOperator(session_key)

def get_abstract_operator(session_key):
    return BaseAbstractOperator(session_key)
