from  django import forms

class BaseForm(forms.ModelForm):
    """Base form class providing default field exclusions and widget styling.

    Attributes:
        deafault_exclude_fields (list): Fields automatically excluded from the form.
        exclude_fields (list): Additional fields to exclude dynamically.
    """
    deafault_exclude_fields = [
        "created_at",
        "updated_at",
        "deactivated_at",
        "created_by",
        "updated_by",
        "deactivated_by",
    ]
    exclude_fields = []
    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._form_process()

    def clean(self):
        cleaned_data = super().clean()
        # Add custom validation logic here
        return cleaned_data

    def exclude(self, *fields: str):
        """Dynamically add fields to the exclusion list and re-process the form.

        Args:
            *fields (str): Field names to exclude.
        """
        if fields:
            self.exclude_fields.extend(fields)
            self._form_process()

    def _form_process(self):
        """Internal method to process exclusions and apply standard Bootstrap CSS classes to widgets."""
        exclude_fields = self.deafault_exclude_fields
        if self.exclude_fields:
            exclude_fields += self.exclude_fields
        for field in exclude_fields:
            self.fields.pop(field, None)
        for field_name, field in self.fields.items():
            widget_name = field.widget.__class__.__name__
            if widget_name in [
                "CheckboxInput",
                "CheckboxSelectMultiple",
                "RadioSelect",
            ]:
                field.widget.attrs.update({"class": "form-check-input"})
            else:
                # Standard inputs get form-control
                field.widget.attrs.update({"class": "form-control"})
