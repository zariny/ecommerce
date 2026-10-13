from enum import Enum
import datetime as dt
import strawberry


@strawberry.interface
class MetaDataType:
    metadata: strawberry.scalars.JSON | None = strawberry.field(
        default=None, description="Some metadata stored in json structure."
    )


@strawberry.interface
class ChartAndPlotType:
    title: str | None = strawberry.field(
        default=None, description="Suggested chart title."
    )
    generated_at: dt.datetime = strawberry.field(
        default="Generation time (useful for caching/display)."
    )


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
class DateChart(ChartAndPlotType, MetaDataType):
    granularity: Granularity = strawberry.field(description="X axis granularity.")
    series: list[SeriesMeta] = strawberry.field(
        description="All series, in display order."
    )
    buckets: list[Bucket] = strawberry.field(
        description="X axis points in ascending time order."
    )


@strawberry.type
class SimpleChart(ChartAndPlotType):
    lines: list["NumericPoint"] = strawberry.field(
        description="X axis points in ascending order."
    )


@strawberry.type
class NumericPoint:
    label: str = strawberry.field(description="Human-readable name shown to the user.")
    num: int = strawberry.field(description="Raw count, number ")
