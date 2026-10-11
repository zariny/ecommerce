import strawberry
import strawberry_django
from ..models import Order, OrderStatusPipeline
from utils.charts import ChartData, Granularity, DataPoint, Bucket, SeriesMeta
from django.db.models import Max, Count, functions
import datetime as dt
from datetime import timedelta
from itertools import groupby


@strawberry.type
class OrderQuery:
    @strawberry_django.field
    def order_status_moving_window(self) -> ChartData:
        title = "Order status over the last 6 weeks"
        series = [SeriesMeta(key=s.value, label=s.value) for s in OrderStatusPipeline]

        last = Order.objects.aggregate(last=Max("date_placed"))["last"]
        if last is None:
            return ChartData(
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

        return ChartData(
            title=title,
            granularity=Granularity.WEEK,
            series=series,
            buckets=buckets,
            generated_at=dt.datetime.now(dt.UTC),
        )
