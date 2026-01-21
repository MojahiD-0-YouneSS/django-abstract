# Import ALL models from your sub-modules here
# This tells Django: "These models belong to the 'django_abstract' app"

from django_abstract.client.models import (
    AbstractBannedUser, 
    AbstractSessionMetrics,
    AbstractGuestIdentity, 
    AbstractSessionLink,
    AbstractGuestModeRegestry,
    AbstractAuthenticatedModeRegestry,
)
from django_abstract.log.models import (
    SystemErrorLog,
    FeatureToggle,
    AdminActionLog,
    GenericActivityLog,
)

# Note: Abstract models won't create tables, but Concrete ones (like GenericActivityLog) will.