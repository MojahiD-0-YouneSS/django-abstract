from django_abstract.client.services.creators import (
    AbstractGuestIdentityCreator,
    AbstractSessionLinkCreator,
    AbstractBannedUserCreator,
    AbstractClientSessionMetricsCreator,

    )

class AbstractClientCreateDependency:
    def __init__(self):
        self.create_abstract_guest_identity = AbstractGuestIdentityCreator()
        self.create_abstract_session_link = AbstractSessionLinkCreator()
        self.create_abstract_banned_user=AbstractBannedUserCreator()
        self.create_abstract_client_session_metrics=AbstractClientSessionMetricsCreator()

def get_create_manager():
    return AbstractClientCreateDependency()
