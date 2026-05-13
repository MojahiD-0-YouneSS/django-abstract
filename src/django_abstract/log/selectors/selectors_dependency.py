from django_abstract.base.base_dependency import BaseCreateDependency


class AbstractLogSelectDependency(BaseCreateDependency):
    """dependency grouping for logging selectors"""
    app_name = 'django_abstracr_log'


def get_log_dependency():
    return AbstractLogSelectDependency()
