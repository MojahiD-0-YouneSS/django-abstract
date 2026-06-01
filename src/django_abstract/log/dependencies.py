from django_abstract.base.base_dependency import BaseDependency

class AbstractLoggingDependency(BaseDependency):
    """Dependency injection container for the logging module.

    Attributes:
        app_name (str): The name of the app context ('django_abstract_log').
        domain (str): The functional domain ('logging').
        description (str): Brief description of the dependency's purpose.
    """
    app_name='django_abstract_log'
    domain='logging'
    description = 'logs events to database'
    def __init__(self,registry=None):
        """Initialize the AbstractLoggingDependency.

        Args:
            registry (dict, optional): The dependency registry to use. Defaults to None.
        """
        super().__init__(registry)
        self.normalize_dependency()

   

def get_dependency_manager():
    return AbstractLoggingDependency()