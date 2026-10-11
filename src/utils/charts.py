from enum import Enum
import datetime as dt
import strawberry


@strawberry.enum(description="Granularity of the X axis.")
class Granularity(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@strawberry.type(description="A series in the chart (e.g. one basket status).")
class SeriesMeta:
    key: str = strawberry.field(
        description="Stable identifier used by frontend logic (e.g. 'Submitted')."
    )
    label: str = strawberry.field(description="Human-readable name shown to the user.")


@strawberry.type(description="Value of one series at one point on the X axis.")
class DataPoint:
    series_key: str = strawberry.field(description="Must match one of SeriesMeta.key.")
    value: int = strawberry.field(
        description="Raw count. The frontend computes percentages."
    )


@strawberry.type(
    description="One point on the X axis (e.g. a week) with the values of all series."
)
class Bucket:
    key: str = strawberry.field(
        description="Machine-readable bucket id, e.g. '2026-07-06'."
    )
    label: str = strawberry.field(description="Display label, e.g. 'Week of Jul 6'.")
    start: dt.datetime = strawberry.field(description="Bucket start (inclusive).")
    end: dt.datetime = strawberry.field(description="Bucket end (exclusive).")
    total: int = strawberry.field(
        description="Sum of all series values in this bucket."
    )
    points: list[DataPoint] = strawberry.field(
        description="One entry per series (zeros included)."
    )


@strawberry.type(
    description="Generic output for categorical/time charts (stacked bar, line, area, ...)."
)
class ChartData:
    title: str | None = strawberry.field(
        default=None, description="Suggested chart title."
    )
    granularity: Granularity = strawberry.field(description="X axis granularity.")
    series: list[SeriesMeta] = strawberry.field(
        description="All series, in display order."
    )
    buckets: list[Bucket] = strawberry.field(
        description="X axis points in ascending time order."
    )

    generated_at: dt.datetime = strawberry.field(
        default="Generation time (useful for caching/display)."
    )
