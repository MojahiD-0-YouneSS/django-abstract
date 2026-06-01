import uuid
from django.db import models
from django.conf import settings
from django_abstract.base.base_model import BaseModel  # Assuming internal reference
from django_abstract.log.dependencies import AbstractLoggingDependency  
from django_abstract.registry import creator_selector

@creator_selector(dependency=AbstractLoggingDependency)
class SystemErrorLog(BaseModel):
    """Universal Error Log.
    Captures stack traces and error details from ANY app.

    Attributes:
        error_code (str, optional): A specific error code for the exception.
        error_message (str): The human-readable error message.
        stack_trace (str): The stack trace of the error.
        service_name (str): The name of the service where the error occurred.
        app_name (str): The name of the app where the error occurred.
        method_name (str, optional): The name of the method where the error occurred.
        service_function_name (str): The name of the function where the error occurred.
        action (str): The action that caused the error.
        environment (str): The environment where the error occurred.
        severity (str): The severity of the error.
        reported_by (str, optional): The user who reported the error.
        resolved (bool): Indicates if the error has been resolved.
        resolved_at (datetime, optional): Time when the error was resolved.
        notes (str, optional): Additional notes regarding the error.
    """
    SEVERITY_CHOICES = [
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')
    ]
    ENVIRONMENT_CHOICES = [
        ('development', 'Development'), ('staging', 'Staging'), ('production', 'Production')
    ]

    error_code = models.CharField(max_length=100, null=True, blank=True)
    error_message = models.TextField()
    stack_trace = models.TextField(blank=True)
    
    # Context
    service_name = models.CharField(max_length=250)
    app_name = models.CharField(max_length=250)
    method_name = models.CharField(max_length=250, null=True, blank=True)
    service_function_name = models.CharField(max_length=250)
    action = models.CharField(max_length=250, blank=True)
    environment = models.CharField(max_length=50, choices=ENVIRONMENT_CHOICES, default='development')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    
    # Resolution
    reported_by = models.CharField(max_length=250, null=True, blank=True,)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "System Error Log"
        ordering = ['-created_at'] # Assuming BaseModel has created_at

    def __str__(self):
        return f"[{self.severity.upper()}] {self.error_code or 'Error'}: {self.error_message[:50]}"

@creator_selector(dependency=AbstractLoggingDependency)
class FeatureToggle(BaseModel):
    """Universal Feature Flag system.
    Useful for any app to turn features on/off without deployment.

    Attributes:
        feature_name (str): The unique name of the feature.
        description (str, optional): Description of the feature.
        is_enabled (bool): Whether the feature is active.
        toggle_type (str): Type of toggle (global, user, group).
    """
    feature_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    is_enabled = models.BooleanField(default=False)
    toggle_type = models.CharField(
        max_length=50,
        choices=[('global', 'Global'), ('user', 'User-Based'), ('group', 'Group-Based')],
        default='global'
    )

    def __str__(self):
        status = "ON" if self.is_enabled else "OFF"
        return f"{self.feature_name} [{status}]"

@creator_selector(dependency=AbstractLoggingDependency)
class AdminActionLog(BaseModel):
    """Generic Audit Log for Admin actions.
    Uses Generic Foreign Key logic conceptually to link to anything.

    Attributes:
        admin (ForeignKey): Reference to the admin user who performed the action.
        action_type (str): Type of action performed (e.g., Update, Delete).
        action_description (str): Detailed description of the action.
        related_object_type (str): The type of object affected.
        related_object_id (str): The ID of the affected object.
        status (str): Outcome status (success or failure).
        performed_at (datetime): Timestamp of the action.
    """
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=100)  # e.g., "Update", "Delete"
    action_description = models.TextField()
    
    # Loose coupling to target object
    related_object_type = models.CharField(max_length=50) 
    related_object_id = models.CharField(max_length=255) # Changed to Char for UUID support
    
    status = models.CharField(max_length=20, choices=[('success', 'Success'), ('failure', 'Failure')])
    performed_at = models.DateTimeField(auto_now_add=True)

class LogEvent(models.Model):
    """
    Immutable Event Stream.
    Good for 'Event Sourcing' patterns or simple system history.
    """
    EVENT_TYPES = [
        ('user_action', 'User Action'),
        ('admin_action', 'Admin Action'),
        ('system', 'System'),
        ('security', 'Security'),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    action = models.CharField(max_length=255)
    metadata = models.JSONField(blank=True, null=True) # Stores the details
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.event_type}] {self.action} at {self.created_at}"

# --- OPTIONAL (Keep if you want built-in user tracking) ---

@creator_selector(dependency=AbstractLoggingDependency)
class GenericActivityLog(BaseModel):
    """
    A stripped-down version of your ActivityLog.
    Removes specific business logic, keeps HTTP context.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    
    # Generic payload instead of specific columns
    activity_type = models.CharField(max_length=100) 
    details = models.JSONField(default=dict) # Store "Cart ID" or "Product ID" here dynamically
    

    