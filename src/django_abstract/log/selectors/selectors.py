from django_abstract.base.base_selector import BaseSelector
from django_abstract.registry import register_selector
from django_abstract.log.dependencies import AbstractLoggingDependency


from django_abstract.log.models import (
    SystemErrorLog,
    FeatureToggle,
    AdminActionLog,
    GenericActivityLog,
)

@register_selector(dependency=AbstractLoggingDependency)
class SystemErrorLogSelector(BaseSelector):
    """Selector for retrieving SystemErrorLog records."""

    def __init__(self,):
        super().__init__(SystemErrorLog)

@register_selector(dependency=AbstractLoggingDependency)
class FeatureToggleSelector(BaseSelector):
    """Selector for retrieving FeatureToggle records."""

    def __init__(self,):
        super().__init__(FeatureToggle)

@register_selector(dependency=AbstractLoggingDependency)
class AdminActionLogSelector(BaseSelector):

    def __init__(self,):
        super().__init__(AdminActionLog)

@register_selector(dependency=AbstractLoggingDependency)
class GenericActivityLogSelector(BaseSelector):

    def __init__(self,):
        super().__init__(GenericActivityLog)
