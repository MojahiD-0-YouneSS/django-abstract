from django.db import models
from django_abstract.base.base_model import BaseModel

class DummyModel(BaseModel):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = "tests"
