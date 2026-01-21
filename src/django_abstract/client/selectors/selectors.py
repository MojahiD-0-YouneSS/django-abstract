from django_abstract.base_selector import BaseSelector
from django_abstract.client.models import (
    AbstractGuestIdentity,
    AbstractSessionLink,
    AbstractBannedUser,
    AbstractClientSessionMetrics,    
)

 

class AbstractGuestIdentitySelector(BaseSelector):
    def __init__(self):
        super().__init__(AbstractGuestIdentity)


class AbstractSessionLinkSelector(BaseSelector):
    def __init__(self):
        super().__init__(AbstractSessionLink)

class AbstractBannedUserSelector(BaseSelector):
    def __init__(self):
        super().__init__(AbstractBannedUser)

class AbstractClientSessionMetricsSelector(BaseSelector):
    def __init__(self):
        super().__init__(AbstractClientSessionMetrics)
