from itertools import groupby
import datetime as dt
import strawberry
import strawberry_django
from ..models import Order, OrderStatusPipeline
from utils.charts import DateChart, Granularity, DataPoint, Bucket, SeriesMeta
from django.db.models import Max, Count, functions, Avg
from datetime import timedelta


@strawberry.type
class OrderQuery:
    @strawberry_django.field
    def order_status_moving_window(self) -> DateChart:
        title = "Order status over the last 6 weeks"
        series = [SeriesMeta(key=s.value, label=s.value) for s in OrderStatusPipeline]

        last = Order.objects.aggregate(last=Max("date_placed"))["last"]
        if last is None:
            return DateChart(
                title=title,
                granularity=Granularity.WEEK,
                series=series,
                buckets=[],
                generated_at=dt.datetime.now(dt.UTC),
            )

        last_week_start = (last - timedelta(days=last.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start_date = last_week_start - timedelta(weeks=5)
        end_date = last_week_start + timedelta(weeks=1)  # exclusive

        qs = (
            Order.objects.filter(date_placed__gte=start_date, date_placed__lt=end_date)
            .annotate(week=functions.TruncWeek("date_placed"))
            .values("week", "status")
            .annotate(count=Count("pk"))
            .order_by("week", "status")
        )

        count_by_week = {
            week: {r["status"]: r["count"] for r in rows}
            for week, rows in groupby(qs, key=lambda r: r["week"])
        }

        buckets = []
        for i in range(6):
            week = start_date + timedelta(weeks=i)
            counts = count_by_week.get(week, {})
            points = [
                DataPoint(series_key=s.value, value=counts.get(s.value, 0))
                for s in OrderStatusPipeline
            ]
            buckets.append(
                Bucket(
                    key=week.date().isoformat(),
                    label=f"Week of {week:%b %d}",
                    start=week,
                    end=week + timedelta(weeks=1),
                    total=sum(p.value for p in points),
                    points=points,
                )
            )

        return DateChart(
            title=title,
            granularity=Granularity.WEEK,
            series=series,
            buckets=buckets,
            generated_at=dt.datetime.now(dt.UTC),
        )

    @strawberry_django.field
    def complete_order_moving_window(self) -> DateChart:
        title = "Complete orders over the last 90 days"

        series = [SeriesMeta(key=OrderStatusPipeline.COMPLETE.value, label="Complete")]

        last = Order.objects.aggregate(last=Max("date_placed"))["last"]
        if last is None:
            return DateChart(
                title=title,
                granularity=Granularity.DAY,
                series=series,
                buckets=[],
                generated_at=dt.datetime.now(dt.UTC),
            )
        start_day = (last - timedelta(days=90)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        last_day = last.replace(hour=0, minute=0, second=0, microsecond=0)
        num_days = (last_day - start_day).days + 1
        end_exclusive = last_day + timedelta(days=1)

        qs = (
            Order.objects.filter(
                status=OrderStatusPipeline.COMPLETE,
                date_placed__gte=start_day,
                date_placed__lt=end_exclusive,
            )
            .annotate(day=functions.TruncDay("date_placed"))
            .values("day")
            .annotate(count=Count("pk"))
            .order_by("day")
        )

        count_by_day = {row["day"]: row["count"] for row in qs}
        average = qs.aggregate(avg=Avg("count"))["avg"]

        annotations: dict = {}
        if average is not None:
            annotations["yaxis"] = [{"label": "Average", "value": average}]

        buckets = []
        for i in range(num_days):
            day = start_day + timedelta(days=i)
            count = count_by_day.get(day, 0)
            buckets.append(
                Bucket(
                    key=day.date().isoformat(),
                    label=f"{day:%b %d}",
                    start=day,
                    end=day + timedelta(days=1),
                    total=count,
                    points=[
                        DataPoint(
                            series_key=OrderStatusPipeline.COMPLETE.value,
                            value=count,
                        )
                    ],
                )
            )

        return DateChart(
            title=title,
            granularity=Granularity.DAY,
            series=series,
            buckets=buckets,
            metadata={"annotations": annotations},
            generated_at=dt.datetime.now(dt.UTC),
        )
