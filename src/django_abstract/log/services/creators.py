from django_abstract.base_creator import BaseCreator

from django_abstract.log.models import (
    SystemErrorLog,
    FeatureToggle,
    AdminActionLog,
    GenericActivityLog,
)

class SystemErrorLogCreator(BaseCreator):

    def __init__(self,):
        super().__init__(SystemErrorLog)

class FeatureToggleCreator(BaseCreator):

    def __init__(self,):
        super().__init__(FeatureToggle)

class AdminActionLogCreator(BaseCreator):

    def __init__(self,):
        super().__init__(AdminActionLog)

class GenericActivityLogCreator(BaseCreator):

    def __init__(self,):
        super().__init__(GenericActivityLog)

