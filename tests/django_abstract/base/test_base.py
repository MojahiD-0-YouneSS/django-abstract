import pytest
from django.db import models
from django import forms
from datetime import datetime

# Import the abstract base classes
from django_abstract.base.base_model import BaseModel
from django_abstract.base.base_form import BaseForm
from django_abstract.base.base_exception import CoreException
from django_abstract.base.base_dependency import BaseDependency

# ==========================================
# 1. TEST MODELS (Testing Abstract BaseModel)
# ==========================================


from tests.models import DummyModel


@pytest.mark.django_db
def test_base_model_soft_delete():
    """Test that soft_delete correctly sets flags and timestamps without deleting."""
    instance = DummyModel.objects.create(name="Test Item")

    assert instance.is_active is True
    assert instance.deactivated_at is None
    assert instance.status == "Active"

    # Trigger soft delete
    instance.soft_delete()

    assert instance.is_active is False
    assert instance.deactivated_at is not None
    assert instance.status == "Deactivated"

    # Ensure it still exists in the DB!
    assert DummyModel.objects.count() == 1


@pytest.mark.django_db
def test_base_model_reactivate():
    """Test that reactivate restores the object."""
    instance = DummyModel.objects.create(
        name="Test Item", is_active=False, deactivated_at=datetime.utcnow()
    )

    instance.reactivate()

    assert instance.is_active is True
    assert instance.deactivated_at is None


# ==========================================
# 2. TEST FORMS (Testing Auto-styling)
# ==========================================


class DummyForm(BaseForm):
    class Meta:
        model = DummyModel
        fields = "__all__"


def test_base_form_css_injection():
    """Test that the BaseForm automatically injects Bootstrap CSS classes."""
    form = DummyForm()

    # Check that 'name' got form-control
    assert "class" in form.fields["name"].widget.attrs
    assert form.fields["name"].widget.attrs["class"] == "form-control"

    # Check that boolean fields got form-check-input
    assert "class" in form.fields["is_active"].widget.attrs
    assert form.fields["is_active"].widget.attrs["class"] == "form-check-input"


def test_base_form_excludes_audit_fields():
    """Test that audit fields are popped from the form fields dictionary."""
    form = DummyForm()

    # These should be removed by BaseForm._form_process()
    assert "created_at" not in form.fields
    assert "updated_by" not in form.fields


# ==========================================
# 3. TEST EXCEPTIONS
# ==========================================


def test_core_exception_formatting():
    """Test that CoreException formats its output correctly."""
    context_data = {"user_id": 123, "action": "checkout"}
    try:
        raise CoreException(
            message="Payment Failed", error_code=402, context=context_data
        )
    except CoreException as e:
        error_string = str(e)
        assert "[Error 402]" in error_string
        assert "Payment Failed" in error_string
        assert "Context: {'user_id': 123, 'action': 'checkout'}" in error_string


# ==========================================
# 4. TEST DEPENDENCIES
# ==========================================


def test_base_dependency_registration():
    """Test that dependencies properly register selectors and creators locally."""

    class MyDependency(BaseDependency):
        app_name = "test_app"

    class DummySelector:
        pass

    # Register it
    MyDependency.register_selector("select_item", DummySelector)

    # Check that it exists in the class definition
    assert "select_item" in MyDependency.selectors
    assert MyDependency.selectors["select_item"] == DummySelector

    # Check dynamic instantiation via __getattr__
    dep_instance = MyDependency()
    result = dep_instance.select_item
    assert isinstance(result, DummySelector)
