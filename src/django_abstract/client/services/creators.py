from django_abstract.base_service import BaseCreatorService
from django_abstract.client.models import (
        AbstractGuestIdentity,
        AbstractSessionLink,
        AbstractBannedUser,
        AbstractClientSessionMetrics,    
)

class AbstractGuestIdentityCreator(BaseCreatorService):
    def __init__(self):
        super().__init__(AbstractGuestIdentity,)

class AbstractSessionLinkCreator(BaseCreatorService):
    def __init__(self):
        super().__init__(AbstractSessionLink,)

class AbstractBannedUserCreator(BaseCreatorService):
    def __init__(self):
        super().__init__(AbstractBannedUser,)

class AbstractClientSessionMetricsCreator(BaseCreatorService):
    def __init__(self):
        super().__init__(AbstractClientSessionMetrics,)
