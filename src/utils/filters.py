from django_filters import FilterSet, DateFilter, ChoiceFilter
from rest_framework.exceptions import ValidationError
from datetime import datetime, timedelta


class DateRangeFilterSet(FilterSet):
    # Fields:
    start_date = DateFilter(label="Start Date")
    end_date = DateFilter(label="End Date")

    class Meta:
        abstract = True
        field_name = "created_at"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name = getattr(self.Meta, "field_name", "created_at")

    def get_range(self) -> tuple:
        self.is_valid()
        start = self.form.cleaned_data.get("start_date", None)
        end = self.form.cleaned_data.get("end_date", None)
        if start and end:
            self.range_validation(start, end)
        else:
            start, end = self.get_default_range()
        return start, end

    @property
    def delta(self) -> int:
        start_date, end_date = self.get_range()
        result = end_date - start_date
        return result.days

    def filter_queryset(self, queryset):
        start_date, end_date = self.get_range()

        field_filter = {
            "%s__range" % self.field_name: (start_date, end_date)
        }
        return queryset.filter(**field_filter)

    def range_validation(self, start, end):
        if start >= end:
            raise ValidationError("invalid date range")

    def get_default_range(self):
        end = datetime.today().date()
        start = end - timedelta(days=30)
        return (start, end)
