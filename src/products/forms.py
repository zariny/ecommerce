from django import forms
from django.contrib.admin import widgets
from .models import ProductAttributeValue
from .utils import proper_field


class ProductAttributeValueAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            datatype = self.instance.data_type
            proper_widget = self._get_widget(datatype)
            self.fields["value"] = proper_field(datatype).formfield(widget=proper_widget)


    class Meta:
        model = ProductAttributeValue
        fields = "__all__"


    def _get_widget(self, datatype):
        if datatype == "date":
            return widgets.AdminDateWidget
        if datatype == "time":
            return widgets.AdminTimeWidget
        if datatype == "integer":
            return widgets.AdminIntegerFieldWidget
        return None


