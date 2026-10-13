import strawberry
import strawberry_django
from ..models import Basket
from django.db.models.functions import TruncWeek
from django.db.models import Max, Count
from datetime import timedelta
import datetime as dt
from itertools import groupby
from utils.charts import DateChart, Granularity, SeriesMeta, DataPoint, Bucket


@strawberry.type
class BasketQuery:
    @strawberry_django.field
    def basket_status_moving_window(self) -> DateChart:  # TODO cache result
        statuses = [s for s, _ in Basket.STATUS_CHOICES]

        last = Basket.objects.aggregate(last=Max("date_created"))["last"]
        if last is None:
            return DateChart(
                title="Basket status over the last 6 weeks",
                granularity=Granularity.WEEK,
                series=[SeriesMeta(key=s, label=s) for s in statuses],
                buckets=[],
                generated_at=dt.datetime.now(dt.UTC),
            )

        last_week_start = (last - timedelta(days=last.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start_date = last_week_start - timedelta(weeks=5)
        end_date = last_week_start + timedelta(weeks=1)  # exclusive

        qs = (
            Basket.objects.filter(
                date_created__gte=start_date, date_created__lt=end_date
            )
            .annotate(week=TruncWeek("date_created"))
            .values("week", "status")
            .annotate(count=Count("pk"))
            .order_by("week", "status")
        )

        counts_by_week = {
            week: {r["status"]: r["count"] for r in rows}
            for week, rows in groupby(qs, key=lambda r: r["week"])
        }

        buckets = []
        for i in range(6):
            week = start_date + timedelta(weeks=i)
            counts = counts_by_week.get(week, {})
            points = [DataPoint(series_key=s, value=counts.get(s, 0)) for s in statuses]
            buckets.append(
                Bucket(
                    key=week.date().isoformat(),
                    label=f"Week {i + 1}",
                    start=week,
                    end=week + timedelta(weeks=1),
                    total=sum(p.value for p in points),
                    points=points,
                )
            )

        return DateChart(
            title="Basket status over the last 6 weeks",
            granularity=Granularity.WEEK,
            series=[SeriesMeta(key=s, label=s) for s in statuses],
            buckets=buckets,
            generated_at=dt.datetime.now(dt.UTC),
        )
