from django_abstract.log.services.creators import (
    SystemErrorLogCreator,
    FeatureToggleCreator,
    AdminActionLogCreator,
    GenericActivityLogCreator,
)

class AbstractLogCreateDependency:
    """ a dependency for grouping logging creators"""
    def __init__(self):
        self.create_system_error_log = SystemErrorLogCreator()
        self.create_feature_toggle_log = FeatureToggleCreator()
        self.create_admin_action_log = AdminActionLogCreator()
        self.create_generic_activity_log = GenericActivityLogCreator()
        

def get_creator_manager():
    return AbstractLogCreateDependency()
