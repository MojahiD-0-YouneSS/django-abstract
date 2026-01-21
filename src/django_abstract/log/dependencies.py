from django_abstract.base_dependency import BaseDependency,GLOBAL_REGISTRY

class AbstractLoggingDependency(BaseDependency):
    app_name='django_abstract_log'
    domain='logging'
    description = 'logs events to database'
    def __init__(self,registry=None):
        super().__init__(registry)
        self.normalize_dependency()

   

def get_dependency_manager():
    return AbstractLoggingDependency()