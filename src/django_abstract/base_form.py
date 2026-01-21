from  django import forms

class BaseForm(forms.ModelForm):
    exclude_fields = [ "created_at", "updated_at", "deactivated_at", "is_active", "created_by", "updated_by",]

    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.exclude_fields:
            for field in self.exclude_fields:
                self.fields.pop(field, None)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        # Add custom validation logic here
        return cleaned_data