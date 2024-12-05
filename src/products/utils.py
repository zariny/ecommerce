from django.db import models
from .exceptions import UnsupportedDataTypeError


VALUE_TYPE_CHOICE = [
    ("charactor", "Charactor"),
    ("integer", "Integer"),
    ("float", "Float"),
    ("boolean", "True / False"),
    ("date", "Date"),
    ("datetime", "Date - Time"),
    ("time", "Time"),
]


def proper_field(datatype: str) -> models.Field:
    match datatype:
        case "charactor" | "text":
            field = models.TextField()
        case "integer":
            field = models.IntegerField()
        case "float":
            field = models.FloatField()
        case "boolean":
            field = models.BooleanField()
        case "date":
            field = models.DateField()
        case "datetime":
            field = models.DateTimeField()
        case "time":
            field = models.TimeField()
        case "json":
            field = models.JSONField()
        case _:
            raise UnsupportedDataTypeError

    return field
