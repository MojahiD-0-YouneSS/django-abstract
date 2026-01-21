from django_abstract.base_selector import BaseSelector

from django_abstract.log.models import (
    SystemErrorLog,
    FeatureToggle,
    AdminActionLog,
    GenericActivityLog,
)

class SystemErrorLogSelector(BaseSelector):

    def __init__(self,):
        super().__init__(SystemErrorLog)

class FeatureToggleSelector(BaseSelector):

    def __init__(self,):
        super().__init__(FeatureToggle)

class AdminActionLogSelector(BaseSelector):

    def __init__(self,):
        super().__init__(AdminActionLog)

class GenericActivityLogSelector(BaseSelector):

    def __init__(self,):
        super().__init__(GenericActivityLog)
