from django_abstract.base.base_dependency import BaseCreateDependency


class AbstractLogCreateDependency(BaseCreateDependency):
    """Dependency grouping for logging creators."""
    pass

def get_log_dependency():
    return AbstractLogCreateDependency()
