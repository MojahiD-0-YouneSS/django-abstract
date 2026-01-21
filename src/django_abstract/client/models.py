from django.db import models
from django.conf import settings
from django_abstract.base_model import BaseModel
from django_abstract.registry import creator_selector
from django_abstract.client.dependencies import AbstractClientDependency

@creator_selector(dependency=AbstractClientDependency)
class AbstractGuestIdentity(BaseModel):
    """
    Core identity for an unauthenticated user.
    Linked via the 'guest_device_id' cookie.
    """
    session_key = models.CharField(
        max_length=255, 
        unique=True, 
        db_index=True,
        help_text="The UUID stored in the user's cookie."
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    last_active_at = models.DateTimeField(auto_now=True)
    
    # Conversion Tracking
    is_converted = models.BooleanField(default=False)
    converted_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, blank=True, 
        on_delete=models.SET_NULL,
        related_name='guest_history'
    )

    class Meta:
        indexes = [models.Index(fields=['session_key'])]

    def __str__(self):
        return f"Guest: {self.session_key}"

@creator_selector(dependency=AbstractClientDependency)
class AbstractSessionLink(BaseModel):
    """
    The 'Memory Bridge'.
    Links a Guest Session Key to an Authenticated User.
    Used to merge carts/history when a user logs in.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='session_links'
    )
    abstract_guest_user = models.ForeignKey(
        'AbstractGuestIdentity', 
        on_delete=models.CASCADE,
        related_name='guest_user_links'
    )
    curent_session_key = models.CharField(max_length=255, db_index=True)
    previous_session_key = models.CharField(max_length=255, db_index=True)
    merged_at = models.DateTimeField(auto_now_add=True)
    session_count = models.IntegerField(default=1)
    # Metadata about the merge context
    shared_device_hash = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('user', 'abstract_guest_user')
        
@creator_selector(dependency=AbstractClientDependency)
class AbstractBannedUser(BaseModel):
    session_key = models.CharField(
        max_length=100,
        db_index=True,
        help_text="The user's session key whose preferences are being tracked."
    )
    reason = models.TextField(
        help_text="The reason for banning the user."
    )
    banned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when the user was banned."
    )
    banned_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date and time until the ban is active. Leave blank for permanent bans."
    )

    def __str__(self):
        return f"Banned User: {self.user.username}"

    def is_ban_active(self):
        """
        Check if the ban is still active.
        """
        from django.utils.timezone import now
        return self.banned_until is None or self.banned_until > now()

    def lift_ban(self):
        """
        Remove the ban from the user.
        """
        self.delete()

@creator_selector(dependency=AbstractClientDependency)
class AbstractSessionMetrics(BaseModel):
    session_key = models.CharField(
        max_length=100,
        db_index=True,
        help_text="The user's session key whose preferences are being tracked."
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    shared_device_hash = models.CharField(max_length=255, db_index=True)
    referrer = models.CharField(max_length=255, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    pages_visited = models.PositiveIntegerField(default=0)
    interactions_count = models.PositiveIntegerField(default=0)
    conversion_occurred = models.BooleanField(default=False)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        unique_together = ('ip_address', 'session_key', 'start_time')
        ordering = ['-start_time']
        
@creator_selector(dependency=AbstractClientDependency)
class AbstractGuestModeRegestry(BaseModel):
    user =models.CharField(max_length=250, )
    system_id = models.CharField(max_length=250, )
    is_blocked =  models.BooleanField(default=False)
    operation_history = models.JSONField(default=dict)
    def __str__(self,):
        return self.system_id

@creator_selector(dependency=AbstractClientDependency)
class AbstractAuthenticatedModeRegestry(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authenticated_mode'
    )
    guest_mode_regestry =  models.ForeignKey(
       'AbstractGuestModeRegestry',
        on_delete=models.CASCADE,
        related_name='previous_Guest_mode'
    )
    system_id = models.CharField(max_length=250, )
    is_blocked =  models.BooleanField(default=False)
    operation_history = models.JSONField(default=dict)

    def __str__(self,):
        return self.system_id