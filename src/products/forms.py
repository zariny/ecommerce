from django import forms
from . import models


class ProductAttributeValueChangeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        proper_field = self.instance.proper_field
        proper_form = proper_field().formfield()
        self.fields["value"] = proper_form


    class Meta:
        model = models.ProductAttributeValue
        fields = "__all__"
