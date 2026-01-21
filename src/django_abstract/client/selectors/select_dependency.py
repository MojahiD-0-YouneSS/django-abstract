from django_abstract.client.selectors import (
    AbstractGuestIdentitySelector,
    AbstractSessionLinkSelector,
    AbstractBannedUserSelector,
    AbstractClientSessionMetricsSelector,
    )
    
class AbstractClientSelectDependency:
    def __init__(self):
        self.select_abstract_guest_identity_selector = AbstractGuestIdentitySelector()
        self.select_abstract_session_link_selector = AbstractSessionLinkSelector()
        self.select_abstract_banned_user=AbstractBannedUserSelector()
        self.select_abstract_client_session_metrics=AbstractClientSessionMetricsSelector()

def get_select_manager():
    return AbstractClientSelectDependency()
