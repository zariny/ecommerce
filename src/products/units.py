from enum import Enum

from django.db import models


class DistanceUnits(models.TextChoices):
    MM = "MM", "Millimeter"
    CM = "CM", "Centimeter"
    DM = "DM", "Decimeter"
    M = "M", "Meter"
    KM = "KM", "Kilometers"
    INCH = "INCH", "Inch"


class WeightUnits(models.TextChoices):
    G = "G", "Gram"
    LB = "LB", "Pound"
    OZ = "OZ", "Ounce"
    KG = "KG", "kg"


class AreaUnits(models.TextChoices):
    SQ_MM = "SQ_MM", "Square millimeter"
    SQ_CM = "SQ_CM", "Square centimeters"
    SQ_DM = "SQ_DM", "Square decimeter"
    SQ_M = "SQ_M", "Square meters"
    SQ_INCH = "SQ_INCH", "Square inches"


MeasurementUnits: type[Enum] = models.TextChoices(
    "Units",
    [
        (m.name, (m.value, m.label))
        for e in (DistanceUnits, WeightUnits, AreaUnits)
        for m in e
    ],
)
