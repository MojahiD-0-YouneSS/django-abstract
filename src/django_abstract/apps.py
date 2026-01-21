from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_abstract'
    # Human readable name for the Admin panel
    verbose_name = "Enterprise Abstract Layer"
    
    # Auto-field default (Good practice to set this)
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # This is where you import signals to ensure they are registered
        import django_abstract.signals
