from django.core.exceptions import ValidationError
from django.db import models
from .utils import proper_field


class DynamicValueField(models.JSONField):
    def clean(self, value, model_instance, datatype=None):
        if datatype is None:
            datatype = model_instance.data_type
        field = proper_field(datatype)

        try:
            value = field.clean(value, model_instance)
        except ValidationError as e:
            message = e.message % e.params
            raise ValidationError("Validation failed for %s, %s" % (field.get_internal_type(), message))
        except TypeError:
            raise ValidationError("Failed to Converting data to (%s) type." % datatype)

        if self._is_datetime(datatype):
            value = str(value)

        value = self._json_storage_schema(datatype, value)
        return super().clean(value, model_instance)

    def from_db_value(self, value, expression, connection):
        value = super().from_db_value(value, expression, connection)
        datatype, value = value["datatype"], value["value"]
        return self._conversion(datatype, value)

    def _is_datetime(self, datatype):
        return True if datatype in ("date", "datetime", "time") else False

    def _json_storage_schema(self, datatype, value):
        schema = {
            "datatype": datatype,
            "value": value
        }
        return schema

    def _conversion(self, datatype, value):
        if self._is_datetime(datatype):
            value = proper_field(datatype).to_python(value)
        return value
