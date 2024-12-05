from django import forms
from .models import ProductAttributeValue
from .utils import proper_field


class ProductAttributeValueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields["value"] = proper_field(self.instance.data_type).formfield()

    class Meta:
        model = ProductAttributeValue
        fields = "__all__"
