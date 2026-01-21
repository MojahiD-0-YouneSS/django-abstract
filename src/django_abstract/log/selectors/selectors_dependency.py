from django_abstract.log.selectors.selectors import (
    SystemErrorLogSelector,
    FeatureToggleSelector,
    AdminActionLogSelector,
    GenericActivityLogSelector,
)

class AbstractLogSelectDependency:
    """dependency grouping for logging selectors"""
    def __init__(self):
        self.select_client_activity_log = SystemErrorLogSelector()
        self.select_system_error_log = FeatureToggleSelector()
        self.select_admin_action_log = AdminActionLogSelector()
        self.select_admin_note = GenericActivityLogSelector()
      
def get_selector_manager():
    return AbstractLogSelectDependency()
