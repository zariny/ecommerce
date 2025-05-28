from datetime import datetime, timedelta
from django.utils.timezone import make_aware
import random


def random_datetime(start=None, end=None):
    if start is None or end is None:
        end = datetime.now()
        start = end - timedelta(days=60)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    result = start + timedelta(seconds=random_seconds)
    return make_aware(result)
