from django_abstract.base.base_creator import BaseCreator
from django_abstract.registry import register_creator
from django_abstract.log.dependencies import AbstractLoggingDependency

from django_abstract.log.models import (
    SystemErrorLog,
    FeatureToggle,
    AdminActionLog,
    GenericActivityLog,
)

@register_creator(dependency=AbstractLoggingDependency)
class SystemErrorLogCreator(BaseCreator):

    def __init__(self,):
        super().__init__(SystemErrorLog)

@register_creator(dependency=AbstractLoggingDependency)
class FeatureToggleCreator(BaseCreator):

    def __init__(self,):
        super().__init__(FeatureToggle)

@register_creator(dependency=AbstractLoggingDependency)
class AdminActionLogCreator(BaseCreator):

    def __init__(self,):
        super().__init__(AdminActionLog)

@register_creator(dependency=AbstractLoggingDependency)
class GenericActivityLogCreator(BaseCreator):

    def __init__(self,):
        super().__init__(GenericActivityLog)
