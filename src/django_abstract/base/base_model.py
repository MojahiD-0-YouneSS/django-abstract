from django.db import models
from django.utils import timezone
from uuid import uuid4
from django.conf import settings

class BaseModel(models.Model):
    """An abstract base model with common fields for tracking creation, updates, soft deletion, and additional metadata.

    Attributes:
        id (UUIDField): Primary key, defaults to a generated UUID.
        created_at (DateTimeField): Automatically set to the time of creation.
        deactivated_at (DateTimeField): Time when the record was soft-deleted, null if active.
        updated_at (DateTimeField): Automatically updated to the current time on save.
        is_active (BooleanField): Indicates if the record is active. Defaults to True.
        is_disabled (BooleanField): Indicates if the record is disabled. Defaults to False.
        is_deactivated (BooleanField): Indicates if the record is deactivated. Defaults to False.
        created_by (ForeignKey): Reference to the user who created the record.
        updated_by (ForeignKey): Reference to the user who last updated the record.
        deactivated_by (ForeignKey): Reference to the user who deactivated the record.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_disabled = models.BooleanField(default=False)
    is_deactivated = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_created_by",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_updated_by",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    deactivated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_deactivated_by",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def soft_delete(self):
        """Soft delete the record by deactivating it and setting the `deactivated_at` timestamp.

        Sets the `is_active` attribute to False and updates the `deactivated_at`
        attribute to the current time. Saves the instance to the database.

        Returns:
            None
        """
        self.is_active = False
        self.deactivated_at = timezone.now()
        self.save()

    def reactivate(self):
        """Reactivate the record by setting it as active and clearing the `deactivated_at` timestamp.

        Sets the `is_active` attribute to True and resets the `deactivated_at`
        attribute to None. Saves the instance to the database.

        Returns:
            None
        """
        self.is_active = True
        self.deactivated_at = None
        self.save()

    @property
    def status(self):
        """Return a human-readable status for the object.

        Returns:
            str: "Active" if the record is active, otherwise "Deactivated".
        """
        return "Active" if self.is_active else "Deactivated"

    class Meta:
        abstract = True  # Ensure this model is abstract
        ordering = ['-created_at']  # Default ordering by creation date descending
        get_latest_by = 'created_at'  # Default latest field for queries
