import datetime as dt
from django.db.models import Max, Count, functions, Avg
import strawberry_django
import strawberry
from . import types
from ..models import User
from utils.charts import DateChart, DataPoint, Granularity, SeriesMeta, Bucket
from utils.relay import CursorConnection


@strawberry.type
class AccountQuery:
    users: CursorConnection[types.UserType] = strawberry_django.connection()
    user: types.UserType = strawberry_django.node()
    groups: CursorConnection[types.GroupType] = strawberry_django.connection()
    group: types.GroupType = strawberry_django.node()

    @strawberry.field
    async def me(self, info: strawberry.types.Info) -> types.UserType | None:
        user = await info.context.request.auser()
        if not user or not user.is_authenticated:
            return None
        return user

    @strawberry_django.field
    def user_joined_moving_window(self) -> DateChart:  # TODO cache me!
        title = "New users over the last 90 days"
        series = [SeriesMeta(key="joined", label="Joined")]
        last = User.objects.aggregate(last=Max("date_joined"))["last"]

        if last is None:
            return DateChart(
                title=title,
                metadata=None,
                generated_at=dt.datetime.now(dt.UTC),
                granularity=Granularity.DAY,
                series=series,
                buckets=[],
            )

        start_day = (last - dt.timedelta(days=90)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        last_day = last.replace(hour=0, minute=0, second=0, microsecond=0)
        num_days = (last_day - start_day).days + 1
        end_exclusive = last_day + dt.timedelta(days=1)

        qs = (
            User.objects.filter(
                date_joined__gte=start_day, date_joined__lt=end_exclusive
            )
            .annotate(day=functions.TruncDay("date_joined"))
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
            day = start_day + dt.timedelta(days=i)
            count = count_by_day.get(day, 0)
            buckets.append(
                Bucket(
                    key=day.date().isoformat(),
                    label=f"{day:%b %d}",
                    start=day,
                    end=day + dt.timedelta(days=1),
                    total=count,
                    points=[DataPoint(series_key="joined", value=count)],
                )
            )

        return DateChart(
            title=title,
            metadata={"annotations": annotations},
            generated_at=dt.datetime.now(dt.UTC),
            granularity=Granularity.DAY,
            series=series,
            buckets=buckets,
        )
