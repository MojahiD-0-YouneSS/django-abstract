from django_abstract.base.base_dependency import BaseCreateDependency


class AbstractLogSelectDependency(BaseCreateDependency):
    """Dependency grouping for logging selectors.

    Attributes:
        app_name (str): The name of the application.
    """
    app_name = 'django_abstracr_log'


def get_log_dependency():
    return AbstractLogSelectDependency()
