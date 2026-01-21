from django_abstract.base_dependency import BaseDependency

class AbstractClientDependency(BaseDependency):

    app_name='django_abstract_client'
    domain='client'
    description = 'manges the client dependencies'

    def __init__(self, registry=None):
        super().__init__(registry)
        self.normalize_dependency()

def get_dependency_manager():
    return AbstractClientDependency()

    
